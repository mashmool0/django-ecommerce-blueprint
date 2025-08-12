from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models

from apps.carts.models import Checkout, CartItem
from apps.orders.models import (
    OrderHeader, OrderLine, Shipment, CouponRedemption, OrderStatus, ShipmentStatus
)
from apps.payments.models import Payment, PaymentStatus


class Command(BaseCommand):
    help = "Creates a demo Order from the most recent Checkout."

    def handle(self, *args, **opts):
        checkout = Checkout.objects.order_by(
            "-created_at").select_related("cart__applied_coupon").first()
        if not checkout:
            self.stdout.write(self.style.WARNING(
                "⚠️ No checkout found. Run `seed_promos_carts` first."))
            return

        cart = checkout.cart
        items = CartItem.objects.filter(cart=cart).select_related(
            "variant", "variant__product")
        if not items:
            self.stdout.write(self.style.WARNING(
                "⚠️ Checkout cart has no items."))
            return

        # naive order_number for demo
        next_no = (OrderHeader.objects.aggregate(
            m=models.Max("order_number"))["m"] or 1000) + 1

        order = OrderHeader.objects.create(
            order_number=next_no,
            user=cart.user,
            phone_e164=str(checkout.phone_number),
            email=checkout.email,
            shipping_address_json=checkout.shipping_address_json,
            status=OrderStatus.PAID,
            subtotal_toman=checkout.items_subtotal_toman,
            discounts_toman=checkout.discounts_total_toman,
            global_discount_toman=checkout.global_discount_toman,
            shipping_fee_toman=checkout.shipping_fee_toman,
            total_payable_toman=checkout.payable_toman,
            cogs_total_toman=0,
            contribution_margin_toman=checkout.payable_toman - 0,  # demo: no COGS
            paid_at=timezone.now(),
            checkout=checkout,
        )

        for it in items:
            OrderLine.objects.create(
                order=order,
                variant=it.variant,
                product_name_fa_snapshot=it.variant.product.name_fa,
                variant_attrs_snapshot={
                    "weight_g": it.variant.weight_grams.grams,
                    "grind": it.variant.grind_type,
                },
                qty=it.qty,
                unit_price_toman=it.unit_price_snapshot_toman,
                line_discount_toman=it.line_discount_toman,
                unit_cogs_toman=0,  # fill when you have COGS
                unit_weight_g=it.variant.weight_grams.grams,
            )

        if cart.applied_coupon:
            CouponRedemption.objects.get_or_create(
                coupon=cart.applied_coupon,
                order=order,
                user=cart.user,
                defaults={
                    "discount_applied_toman": checkout.discounts_total_toman},
            )

        Payment.objects.create(
            order=order,
            status=PaymentStatus.CAPTURED,
            amount_toman=checkout.payable_toman,
            gateway_fee_toman=0,
            authority="DEMO-AUTH",
            ref_id="DEMO-REF",
        )

        Shipment.objects.create(
            order=order,
            status=ShipmentStatus.PENDING,
            carrier="post",
            shipping_fee_toman=checkout.shipping_fee_toman,
            weight_grams=sum((it.variant.weight_grams.grams * it.qty)
                             for it in items),
        )

        self.stdout.write(self.style.SUCCESS(
            f"✅ Order created: {order.id} (number {order.order_number})"))
