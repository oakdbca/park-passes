"""
This management commands deleted and park passes objects from sessions
that have expired and then deletes those sessions.

Usage: ./manage.sh clear_expired_sessions

"""
from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from parkpasses.components.cart.models import Cart
from parkpasses.components.passes.models import Pass


class Command(BaseCommand):
    help = "Clears expired sessions for the park passes system."

    def handle(self, *args, **options):
        now = timezone.now()
        date_today = now.date()
        two_weeks_ago = now - timezone.timedelta(days=14)

        self.stdout.write(
            "Selecting any expired park passes carts (that were last added to more than 14 days ago)"
        )
        if Cart.objects.filter(datetime_last_added_to__lte=two_weeks_ago).exists():
            expired_carts = Cart.objects.filter(
                datetime_last_added_to__lte=two_weeks_ago
            )
            for expired_cart in expired_carts:
                expired_cart_items = expired_cart.items.all()
                for expired_cart_item in expired_cart_items:
                    expired_cart_item.delete()
                expired_cart.delete()
            self.stdout.write(
                self.style.SUCCESS(f"Deleted {len(expired_carts)} Expired carts.")
            )
        else:
            self.stdout.write(
                "No park passes that were added to a cart more than two weeks ago found."
            )

        # A pass may have been in a cart less than 2 weeks but has already expired
        # (i.e. 5 day holiday pass or any short duration pass)
        # So we need to check for those daily and remove them so they are not accidentally purchased.
        self.stdout.write(
            "Selecting any passes that are still in a cart but have expired"
        )
        expired_passes = Pass.objects.exclude(
            cancellation__isnull=False,  # to exclude cancelled passes
        ).filter(
            in_cart=True,
            date_expiry__lte=date_today,
        )
        if expired_passes.exists():
            for expired_pass in expired_passes:
                expired_pass.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {len(expired_passes)} Expired passes still in carts."
                )
            )

        self.stdout.write("Clearing expired django sessions.")
        engine = import_module(settings.SESSION_ENGINE)
        engine.SessionStore.clear_expired()

        self.stdout.write(self.style.SUCCESS("Expired django sessions cleared."))
