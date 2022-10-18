import logging
import os

from rest_framework import serializers

from parkpasses.components.concessions.serializers import InternalConcessionSerializer
from parkpasses.components.discount_codes.serializers import (
    ExternalDiscountCodeSerializer,
)
from parkpasses.components.parks.models import ParkGroup
from parkpasses.components.passes.models import (
    Pass,
    PassCancellation,
    PassTemplate,
    PassType,
    PassTypePricingWindow,
    PassTypePricingWindowOption,
)
from parkpasses.components.retailers.models import RetailerGroup
from parkpasses.components.vouchers.serializers import (
    ExternalVoucherSerializer,
    ExternalVoucherTransactionSerializer,
)

logger = logging.getLogger(__name__)


class PassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "image",
            "display_name",
            "display_order",
        ]
        read_only_fields = [
            "id",
            "slug",
            "name",
            "description",
            "image",
            "display_name",
            "display_order",
        ]


class InternalPassTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassType
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = ["id", "name", "duration", "price"]


class InternalOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTypePricingWindowOption
        fields = "__all__"


class InternalCreatePricingWindowSerializer(serializers.ModelSerializer):
    pricing_options = serializers.ListField(write_only=True)

    class Meta:
        model = PassTypePricingWindow
        fields = [
            "name",
            "pass_type",
            "date_start",
            "date_expiry",
            "pricing_options",
        ]

    def validate(self, data):
        logger.debug(str(data))
        pass_type = data["pass_type"]
        default_options = (
            PassTypePricingWindowOption.get_default_options_by_pass_type_id(
                pass_type.id
            )
        )
        if len(data["pricing_options"]) != len(default_options):
            raise serializers.ValidationError(
                "A price must be provided for each of the default options."
            )
        logger.debug(str(data))
        return data

    def create(self, validated_data):
        options = validated_data.pop("pricing_options")
        logger.debug(str(validated_data))
        pricing_window = PassTypePricingWindow.objects.create(**validated_data)
        default_options = (
            PassTypePricingWindowOption.get_default_options_by_pass_type_id(
                pricing_window.pass_type.id
            )
        )
        for index, default_option in enumerate(default_options):
            PassTypePricingWindowOption.objects.create(
                name=default_option.name,
                duration=default_option.duration,
                price=options[index],
                pricing_window=pricing_window,
            )
        return pricing_window


class InternalPricingWindowSerializer(serializers.ModelSerializer):
    options = InternalOptionSerializer(many=True)
    pass_type_display_name = serializers.ReadOnlyField(source="pass_type.display_name")
    status = serializers.CharField()

    class Meta:
        model = PassTypePricingWindow
        fields = [
            "id",
            "name",
            "pass_type_display_name",
            "pass_type",
            "date_start",
            "date_expiry",
            "options",
            "status",
        ]
        read_only_fields = [
            "pass_type_display_name",
            "status",
        ]
        datatables_always_serialize = [
            "id",
            "options",
        ]


class PassTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassTemplate
        fields = "__all__"


class PassModelCreateSerializer(serializers.ModelSerializer):
    """A base model serializer for passes that allows additonal fields to be submitted for processing"""

    discount_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    voucher_code = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    voucher_pin = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_id = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    concession_card_number = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    sold_via = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        fields = [
            "discount_code",
            "voucher_code",
            "voucher_pin",
            "concession_id",
            "concession_card_number",
            "sold_via",
        ]


class ExternalCreateHolidayPassSerializer(
    PassModelCreateSerializer
):  # user = serializers.IntegerField(write_only=True, required=False, allow_blank=True)
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateAnnualLocalPassSerializer(PassModelCreateSerializer):
    park_group = serializers.PrimaryKeyRelatedField(
        queryset=ParkGroup.objects.all(), many=False
    )

    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "park_group",
            "postcode",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateAllParksPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateGoldStarPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreateDayEntryPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalCreatePinjarOffRoadPassSerializer(PassModelCreateSerializer):
    class Meta(PassModelCreateSerializer.Meta):
        model = Pass
        fields = [
            "id",
            "user",
            "option",
            "first_name",
            "last_name",
            "email",
            "mobile",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "renew_automatically",
            "date_start",
            "processing_status",
            "datetime_created",
            "datetime_updated",
        ] + PassModelCreateSerializer.Meta.fields


class ExternalPassSerializer(serializers.ModelSerializer):
    processing_status_display_name = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )
    price = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    pass_type = serializers.SerializerMethodField()
    pass_type_name = serializers.SerializerMethodField()
    pass_type_image = serializers.CharField(
        source="option.pricing_window.pass_type.image.url"
    )
    park_group = serializers.CharField()
    concession = serializers.SerializerMethodField()
    price_after_concession_applied = serializers.CharField()
    discount_code = serializers.SerializerMethodField()
    price_after_discount_code_applied = serializers.CharField()
    voucher = serializers.SerializerMethodField()
    voucher_transaction = ExternalVoucherTransactionSerializer()
    price_after_voucher_applied = serializers.CharField()

    class Meta:
        model = Pass
        fields = [
            "id",
            "pass_number",
            "option",
            "pass_type",
            "pass_type_name",
            "pass_type_image",
            "price",
            "duration",
            "first_name",
            "last_name",
            "email",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "prevent_further_vehicle_updates",
            "park_group",
            "park_pass_pdf",
            "date_start",
            "date_expiry",
            "renew_automatically",
            "processing_status",
            "processing_status_display_name",
            "datetime_created",
            "datetime_updated",
            "concession",
            "price_after_concession_applied",
            "discount_code",
            "price_after_discount_code_applied",
            "voucher",
            "voucher_transaction",
            "price_after_voucher_applied",
        ]
        read_only_fields = [
            "id",
            "pass_number",
            "pass_type",
            "pass_type_name",
            "price",
            "park_group",
            "date_expiry",
            "park_pass_pdf",
            "processing_status",
            "processing_status_display_name",
            "datetime_created",
            "datetime_updated",
            "concession",
            "price_after_concession_applied",
            "discount_code",
            "price_after_discount_code_applied",
            "voucher",
            "voucher_transaction",
            "price_after_voucher_applied",
        ]

    def get_price(self, obj):
        return f"{obj.option.price:.2f}"

    def get_pass_type(self, obj):
        return obj.option.pricing_window.pass_type.display_name

    def get_pass_type_name(self, obj):
        return obj.option.pricing_window.pass_type.name

    def get_duration(self, obj):
        return f"{obj.option.duration} days"

    def get_concession(self, obj):
        if hasattr(obj, "concession_usage"):
            concession = obj.concession_usage.concession
            serializer = InternalConcessionSerializer(concession)
            return serializer.data
        return None

    def get_discount_code(self, obj):
        if hasattr(obj, "discount_code_usage"):
            discount_code = obj.discount_code_usage.discount_code
            serializer = ExternalDiscountCodeSerializer(discount_code)
            return serializer.data
        return None

    def get_voucher(self, obj):
        if hasattr(obj, "voucher_transaction"):
            voucher = obj.voucher_transaction.voucher
            serializer = ExternalVoucherSerializer(voucher)
            return serializer.data
        return None


class ExternalUpdatePassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pass
        fields = [
            "renew_automatically",
            "vehicle_registration_1",
            "vehicle_registration_2",
            "prevent_further_vehicle_updates",
        ]

    def validate(self, data):
        if data["prevent_further_vehicle_updates"]:
            if data["vehicle_registration_1"]:
                raise serializers.ValidationError(
                    "Updating vehicle registration has been prevented for this pass."
                )
            if data["vehicle_registration_2"]:
                raise serializers.ValidationError(
                    "Updating vehicle registration has been prevented for this pass."
                )
        return data


class RetailerUpdatePassSerializer(serializers.ModelSerializer):
    duration = serializers.CharField(source="option.name", read_only=True)
    date_expiry = serializers.CharField(read_only=True)

    class Meta:
        model = Pass
        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "duration",
            "date_start",
            "date_expiry",
            "vehicle_registration_2",
            "vehicle_registration_2",
        ]


class InternalPassRetrieveSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pass_type_name = serializers.CharField(
        source="option.pricing_window.pass_type.name", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    duration = serializers.CharField(source="option.name")
    park_pass_pdf = serializers.SerializerMethodField()
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.CharField(source="sold_via.name", read_only=True)
    processing_status_display_name = serializers.CharField(
        source="get_processing_status_display", read_only=True
    )
    concession_type = serializers.CharField(
        source="concessionusage.concession.concession_type",
        read_only=True,
        required=False,
    )
    concession_discount_percentage = serializers.CharField(
        source="concessionusage.concession.discount_percentage",
        read_only=True,
        required=False,
    )
    discount_code_used = serializers.CharField(
        source="discountcodeusage.discount_code.code", required=False
    )
    discount_code_discount = serializers.SerializerMethodField(
        read_only=True, required=False
    )
    voucher_number = serializers.CharField(
        source="vouchertransaction.voucher.voucher_number",
        read_only=True,
        required=False,
    )
    voucher_transaction_amount = serializers.CharField(
        source="voucher_transaction.voucher.amount"
    )

    def get_discount_code_discount(self, obj):
        if hasattr(obj, "discountcodeusage"):
            discount = (
                obj.discountcodeusage.discount_code.discount_code_batch.discount_amount
            )
            if discount:
                return f"${discount}"
            discount = (
                obj.discountcodeusage.discount_code.discount_code_batch.discount_percentage
            )
            return f"{discount}% Off"
        return None

    def get_park_pass_pdf(self, obj):
        return os.path.basename(obj.park_pass_pdf.name)

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = [
            "pass_type",
            "pricing_window",
            "sold_via",
            "sold_via_name",
            "pass_type_name",
        ]


class InternalPassSerializer(serializers.ModelSerializer):
    pass_type = serializers.CharField(
        source="option.pricing_window.pass_type", read_only=True
    )
    pricing_window = serializers.CharField(source="option.pricing_window")
    park_pass_pdf = serializers.SerializerMethodField()
    sold_via = serializers.PrimaryKeyRelatedField(queryset=RetailerGroup.objects.all())
    sold_via_name = serializers.CharField(source="sold_via.name", read_only=True)
    processing_status_display_name = serializers.CharField(
        source="status_display", read_only=True
    )

    class Meta:
        model = Pass
        fields = "__all__"
        read_only_fields = ["pass_type", "pricing_window", "sold_via", "sold_via_name"]
        datatables_always_serialize = [
            "id",
        ]

    def get_park_pass_pdf(self, obj):
        return os.path.basename(obj.park_pass_pdf.name)


class InternalPassCancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassCancellation
        fields = "__all__"
