from datetime import date
from uuid import uuid4
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from apps.accounts.models import User
from apps.catalog.models import ProductVariant
from apps.orders.models import OrderHeader
from apps.analytics.models import EventLog, DailyUserSnapshot, DailyInventorySnapshot


class Command(BaseCommand):
    help = "Seeds EventLog + daily snapshots for demo."

    def handle(self, *args, **opts):
        user = User.objects.order_by("date_joined").first()
        if not user:
            self.stdout.write(self.style.WARNING(
                "⚠️ No users. Create a superuser first."))
            return

        anon = uuid4()
        now = timezone.now()

        # Pick a variant
        variant = ProductVariant.objects.select_related("product").first()
        if not variant:
            self.stdout.write(self.style.WARNING(
                "⚠️ No variants. Run `seed_demo` first."))
            return

        # Create a couple of events
        EventLog.objects.create(
            name="Page Viewed",
            timestamp=now,
            anonymous_id=anon,
            utm_json={"utm_source": "google", "utm_medium": "cpc"},
            properties={"url": "/"},
        )
        EventLog.objects.create(
            name="Product Viewed",
            timestamp=now,
            user=user,
            properties={"product_id": str(
                variant.product_id), "variant_id": str(variant.id)},
        )
        EventLog.objects.create(
            name="Add to Cart",
            timestamp=now,
            user=user,
            properties={"variant_id": str(
                variant.id), "qty": 1, "price_toman": 320000},
        )

        order = OrderHeader.objects.order_by("-placed_at").first()
        if order:
            EventLog.objects.create(
                name="Order Paid",
                timestamp=order.paid_at or now,
                user=order.user,
                properties={
                    "order_id": str(order.id),
                    "total_value_toman": order.total_payable_toman,
                    "gateway_fee_toman": order.gateway_fee_toman,
                },
                sent_to_ga=True,
                sent_to_mixpanel=True,
            )

        # User daily snapshot (toy numbers)
        snap_date = date.today()
        total_orders = OrderHeader.objects.filter(user=user).count()
        total_spend = OrderHeader.objects.filter(user=user).aggregate(
            s=models.Sum("total_payable_toman"))["s"] or 0
        first = OrderHeader.objects.filter(user=user).order_by(
            "placed_at").values_list("placed_at", flat=True).first()
        last = OrderHeader.objects.filter(user=user).order_by(
            "-placed_at").values_list("placed_at", flat=True).first()

        DailyUserSnapshot.objects.update_or_create(
            snapshot_date=snap_date,
            user=user,
            defaults=dict(
                total_orders=total_orders,
                total_spend_toman=total_spend,
                first_purchase_at=first,
                last_purchase_at=last,
                rfm_score=4,
                churn_risk="Low",
                lifetime_cogs_toman=0,
                preferred_categories=None,
            ),
        )

        # Inventory daily snapshot for one variant (toy numbers)
        DailyInventorySnapshot.objects.update_or_create(
            snapshot_date=snap_date,
            variant=variant,
            defaults=dict(
                units_on_hand=variant.stock.on_hand if hasattr(
                    variant, "stock") else 50,
                inventory_value_toman=(variant.stock.on_hand if hasattr(
                    variant, "stock") else 50) * 250000,
                sell_through_rate=12.5,
            ),
        )

        self.stdout.write(self.style.SUCCESS(
            "✅ Seeded analytics: events + daily snapshots"))
