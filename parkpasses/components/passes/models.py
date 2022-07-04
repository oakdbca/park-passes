"""
    This module contains the models required to impliment passes.

    - PassType (Local, Holiday, Annual etc.)
    - PassTypePricingWindow (A period of time that specific pricing can be specified)
    - PassTypePricingWindowOption (The duration options for a pass i.e. 5 days, 14 days, etc.)
    - Pass (The pass itself which contains the information required to generate the QR Code)
"""

import logging
import math

import qrcode
from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone

from parkpasses.components.parks.models import Park
from parkpasses.components.passes.exceptions import PassTemplateDoesNotExist
from parkpasses.components.passes.utils import PassUtils
from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.ledger_api_utils import retrieve_email_user
from parkpasses.settings import PASS_TYPES

logger = logging.getLogger(__name__)


def pass_type_image_path(instance, filename):
    """Stores the pass type images in a unique folder

    based on the content type and object_id
    """
    return f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.name}/{filename}"


class PassType(models.Model):
    """A class to represent a pass type"""

    image = models.ImageField(upload_to=pass_type_image_path, null=False, blank=False)
    name = models.CharField(max_length=100)  # Name reserved for system use
    display_name = models.CharField(max_length=50, null=False, blank=False)
    display_order = models.SmallIntegerField(null=False, blank=False)
    display_retailer = models.BooleanField(null=False, blank=False, default=True)
    display_externally = models.BooleanField(null=False, blank=False, default=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pass Type"
        verbose_name_plural = "Pass Types"

    def __str__(self):
        return f"{self.display_name}"


class PassTypePricingWindowManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("pass_type")


class PassTypePricingWindow(models.Model):
    """A class to represent a pass type pricing window

    The default pricing window for a pass type will have no expiry date
    The system will not allow for each pass type to have more than one
    default pricing window.
    """

    objects = PassTypePricingWindowManager()

    name = models.CharField(max_length=50, null=False, blank=False)
    pass_type = models.ForeignKey(
        PassType, on_delete=models.PROTECT, related_name="pricing_window"
    )
    datetime_start = models.DateTimeField()
    datetime_expiry = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pricing Window"

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.datetime_expiry:
            default_pricing_window_count = (
                PassTypePricingWindow.objects.filter(
                    pass_type=self.pass_type,
                    datetime_expiry__isnull=True,
                )
                .exclude(pk=self.pk)
                .count()
            )
            if default_pricing_window_count > 0:
                raise ValidationError(
                    "There can only be one default pricing window for a pass type. \
                    Default pricing windows are those than have no expiry date."
                )
            else:
                if self.datetime_start > timezone.now():
                    raise ValidationError(
                        "The default pricing window start date must be in the past."
                    )
        else:
            if self.datetime_start >= self.datetime_expiry:
                raise ValidationError(
                    "The start date must occur before the expiry date."
                )
            if self.datetime_expiry <= timezone.now():
                raise ValidationError("The expiry date must be in the future.")

        super().save(*args, **kwargs)


class PassTypePricingWindowOptionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("pricing_window", "pricing_window__pass_type")
        )


class PassTypePricingWindowOption(models.Model):
    """A class to represent a pass type pricing window option"""

    objects = PassTypePricingWindowOptionManager()

    pricing_window = models.ForeignKey(
        PassTypePricingWindow, on_delete=models.PROTECT, related_name="option"
    )
    name = models.CharField(max_length=50)  # i.e. '5 days'
    duration = models.SmallIntegerField()  # in days i.e. 5, 14, 28, 365
    price = models.DecimalField(max_digits=7, decimal_places=2, blank=False, null=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Duration Option"
        verbose_name = "Duration Options"

    def __str__(self):
        return f"{self.pricing_window.pass_type.display_name} - {self.name} \
            (Pricing Window: {self.pricing_window.name})"

    @classmethod
    def get_current_options_by_pass_type_id(self, pass_type_id):
        logger.debug("pass_type_id = " + str(pass_type_id))

        try:
            pass_type = PassType.objects.get(id=pass_type_id)
        except ObjectDoesNotExist:
            logger.info(f"No Pass Type Exists with ID: {pass_type_id}.")
            return []

        pricing_windows_for_pass_count = PassTypePricingWindow.objects.filter(
            pass_type=pass_type
        ).count()

        logger.debug(
            "pricing_windows_for_pass_count = " + str(pricing_windows_for_pass_count)
        )

        if 0 == pricing_windows_for_pass_count:
            logger.critical(
                "CRITICAL: There is no default pricing window for Pass Type: {}.".fomat(
                    pass_type
                )
            )
            return []
        # If there is only one pricing window for the pass type it must be the default
        if 1 == PassTypePricingWindow.objects.filter(pass_type=pass_type).count():
            pricing_window = PassTypePricingWindow.objects.get(pass_type=pass_type)
        else:
            # Get any pricing windows that are currently valid excluding the default pricing window
            current_pricing_window_count = (
                PassTypePricingWindow.objects.exclude(datetime_expiry__isnull=False)
                .filter(
                    pass_type=pass_type,
                    datetime_start__lte=timezone.now(),
                    datetime_expiry__gte=timezone.now(),
                )
                .count()
            )
            # If there are none just get the default pricing window
            if 0 == current_pricing_window_count:
                pricing_window = PassTypePricingWindow.objects.get(
                    pass_type=pass_type, datetime_expiry__isnull=True
                )

            elif 1 == current_pricing_window_count:
                pricing_window = PassTypePricingWindow.objects.exclude(
                    datetime_expiry__isnull=False
                ).get(
                    pass_type=pass_type,
                    datetime_start__lte=timezone.now(),
                    datetime_expiry__gte=timezone.now(),
                )
            else:
                # When there are two or more currently valid pricing windows we return the window that
                # started the most recently And log a warning so that admins can be alerted to this.
                # Validation shouldn't allow this sitation to occur but ... just in case.
                logger.warning(
                    f"There are more than one currently valid pricing windows for Pass Type: {pass_type}"
                )
                pricing_window = (
                    PassTypePricingWindow.objects.exclude(datetime_expiry__isnull=False)
                    .filter(
                        pass_type=pass_type,
                        datetime_start__lte=timezone.now(),
                        datetime_expiry__gte=timezone.now(),
                    )
                    .order_by("datetime_start")
                    .last()
                )

        return PassTypePricingWindowOption.objects.filter(pricing_window=pricing_window)


def pass_template_file_path(instance, filename):
    """Stores the pass template documents in a unique folder

    based on the content type and object_id
    """
    return f"{instance._meta.app_label}/{instance._meta.model.__name__}/{instance.version}/{filename}"


class PassTemplate(models.Model):
    """A class to represent a pass template

    The template file field will be the word document that is used as a template to generate a park pass.

    The highest version number will be the template that is used to generate passes.
    """

    template = models.FileField(
        upload_to=pass_template_file_path, null=False, blank=False
    )
    version = models.SmallIntegerField(unique=True, null=False, blank=False)

    class Meta:
        app_label = "parkpasses"
        verbose_name = "Pass Template"
        verbose_name_plural = "Pass Templates"

    def __str__(self):
        return f"{self.template.name} (Version: {self.version}) (Size: {self.pretty_size()})"

    def pretty_size(self):
        size_bytes = self.template.size
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"


class PassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "option",
                "option__pricing_window",
                "option__pricing_window__pass_type",
                "sold_via",
                "cancellation",
            )
        )


class Pass(models.Model):
    """A class to represent a pass"""

    objects = PassManager()

    FUTURE = "FU"
    CURRENT = "CU"
    EXPIRED = "EX"
    CANCELLED = "CA"
    PROCESSING_STATUS_CHOICES = [
        (FUTURE, "Future"),
        (CURRENT, "Current"),
        (EXPIRED, "Expired"),
        (CANCELLED, "Cancelled"),
    ]

    user = models.IntegerField(null=False, blank=False)  # EmailUserRO
    option = models.ForeignKey(PassTypePricingWindowOption, on_delete=models.PROTECT)
    pass_number = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    vehicle_registration_1 = models.CharField(max_length=10, null=True, blank=True)
    vehicle_registration_2 = models.CharField(max_length=10, null=True, blank=True)
    park = models.ForeignKey(Park, on_delete=models.PROTECT, null=True, blank=True)
    datetime_start = models.DateTimeField(null=False, default=False)
    datetime_expiry = models.DateTimeField(null=False, blank=False)
    renew_automatically = models.BooleanField(null=False, blank=False, default=False)
    prevent_further_vehicle_updates = models.BooleanField(
        null=False, blank=False, default=False
    )
    park_pass_pdf = models.FileField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=2, choices=PROCESSING_STATUS_CHOICES, null=True, blank=True
    )
    sold_via = models.ForeignKey(
        RetailerGroup, on_delete=models.PROTECT, null=True, blank=True
    )
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_updated = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Passes"

    def __str__(self):
        return f"{self.pass_number}"

    @property
    def email_user(self):
        return retrieve_email_user(self.user)

    @property
    def pricing_window(self):
        return self.option.pricing_window.name

    @property
    def price(self):
        return self.option.price

    @property
    def pass_type(self):
        return self.option.pricing_window.pass_type.display_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def generate_qrcode(self):
        qr = qrcode.QRCode()
        pass_data_json = serializers.serialize("json", [self])
        # replace this line with the real encryption server at a later date
        encrypted_pass_data = self.imaginary_encryption_endpoint(pass_data_json)
        qr.add_data(encrypted_pass_data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill="black", back_color="white")
        qr_image_path = f"{settings.MEDIA_ROOT}/{self._meta.app_label}/"
        qr_image_path += f"{self._meta.model.__name__}/passes/{self.user}/{self.pk}"
        qr_image.save(f"{qr_image_path}/qr_image.png")
        return f"{qr_image_path}/qr_image.png"

    def generate_park_pass_pdf(self):
        if not PassTemplate.objects.count():
            logger.critical(
                "CRITICAL: The system can not find a Pass Template to use for generating park passes."
            )
            raise PassTemplateDoesNotExist()
        qr_code_path = self.generate_qrcode()
        pass_template = PassTemplate.objects.order_by("-version").first()
        pass_utils = PassUtils()
        pass_utils.generate_pass_pdf_from_docx_template(
            self, pass_template, qr_code_path
        )

    def imaginary_encryption_endpoint(self, json_pass_data):
        return json_pass_data

    def can_cancel_automatic_renewal(self):
        return self.datetime_expiry > timezone.now() + timezone.timedelta(days=1)

    def cancel_automatic_renewal(self):
        if not self.renew_automatically:
            raise ValidationError("This pass does not have automatic renewal enabled.")
        elif not self.can_cancel_automatic_renewal():
            raise ValidationError(
                "You must cancel automatic renewal of a pass at least 24 hours before the pass is due to renew."
            )
        else:
            self.renew_automatically = False
            self.save(update_fields=["renew_automatically"])
            logger.info(
                "Automatic renewal of pass {} has been cancelled.".format(
                    self.pass_number
                )
            )

    def set_processing_status(self):
        if PassCancellation.objects.filter(park_pass=self).count():
            self.processing_status = Pass.CANCELLED
        elif self.datetime_start > timezone.now():
            self.processing_status = Pass.FUTURE
        elif self.datetime_expiry < timezone.now():
            self.processing_status = Pass.EXPIRED
        else:
            self.processing_status = Pass.CURRENT

    def save(self, *args, **kwargs):
        self.datetime_expiry = self.datetime_start + timezone.timedelta(
            days=self.option.duration
        )
        self.set_processing_status()
        email_user = self.email_user
        self.first_name = email_user.first_name
        self.last_name = email_user.last_name
        self.email = email_user.email
        if (
            not self.pass_number
            or "" == self.pass_number
            or 0 == len(self.pass_number.strip())
        ) and self.pk:
            self.pass_number = f"PP{self.pk:06d}"
        super().save(*args, **kwargs)


class PassCancellationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("park_pass")


class PassCancellation(models.Model):
    """A class to represent a pass cancellation

    A one to one related model to store the cancellation reason

    Also, will be able to have a list of files attached to it to justify/explain
    the cancellation"""

    objects = PassCancellationManager()

    park_pass = models.OneToOneField(
        Pass, on_delete=models.PROTECT, related_name="cancellation"
    )
    cancellation_reason = models.TextField(null=False, blank=False)
    datetime_cancelled = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "parkpasses"
        verbose_name_plural = "Pass Cancellations"

    def __str__(self):
        return f"Cancellation for Pass: {self.park_pass.pass_number}(Date Cancelled: {self.datetime_cancelled})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.park_pass.processing_status = Pass.CANCELLED
        self.park_pass.save()


class HolidayPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.HOLIDAY_PASS)
        )


class HolidayPass(Pass):
    """A proxy class to represent a holiday pass"""

    objects = HolidayPassManager()

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass


class LocalParkPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.LOCAL_PARK_PASS)
        )


class LocalParkPass(Pass):
    """A proxy class to represent a local park pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass


class GoldStarPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.GOLD_STAR_PASS)
        )


class GoldStarPass(Pass):
    """A proxy class to represent a gold star pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self, *args, **kwargs):
        # if the user does not have a postal address
        # raise a ValidationError exception
        if True:
            raise ValidationError
        super().save(*args, **kwargs)


class DayEntryPassManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("option", "pricing_window", "pass_type")
            .filter(option__pricing_window__pass_type__name=PASS_TYPES.DAY_ENTRY_PASS)
        )


class DayEntryPass(Pass):
    """A proxy class to represent a day entry pass"""

    class Meta:
        proxy = True
        app_label = "parkpasses"

    def save(self):
        pass
