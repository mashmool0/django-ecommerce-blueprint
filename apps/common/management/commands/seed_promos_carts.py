from django.core.management.base import BaseCommand
from django.utils import timezone
from uuid import uuid4

from apps.catalog.models import (
    GlobalDiscount, Coupon, CouponType, ProductVariant, VariantPrice
)
from apps.carts.models import Cart, CartItem, Checkout, CheckoutStatus


def current_price_toman(variant):
    """Return the latest price for a variant (fallback to 0 if none)."""
    vp = VariantPrice.objects.filter(
        variant=variant).order_by("-created_at").first()
    return vp.price_toman if vp else 0


class Command(BaseCommand):
    help = "Seeds promotions (GlobalDiscount + Coupon) and demo carts & a checkout."

    def handle(self, *args, **opts):
        # 1) Promotions
        gd, _ = GlobalDiscount.objects.get_or_create(
            percent_off=10,
            defaults={"is_active": True, "note": "Demo Nowruz-like sale"},
        )
        # if exists but inactive, turn it on for demo
        if not gd.is_active:
            gd.is_active = True
            gd.save(update_fields=["is_active"])

        coup, _ = Coupon.objects.get_or_create(
            code="WELCOME10",
            defaults={
                "type": CouponType.PERCENT,
                "value": 10,
                "is_active": True,
            },
        )

        # 2) Pick a couple of variants
        variants = list(ProductVariant.objects.select_related(
            "product").order_by("created_at")[:3])
        if len(variants) < 2:
            self.stdout.write(self.style.WARNING(
                "⚠️ Need at least 2 variants. Run `seed_demo` first."))
            return
        v1, v2 = variants[0], variants[1]

        # 3) Build a guest cart
        anon_id = uuid4()
        cart = Cart.objects.create(anonymous_id=anon_id, applied_coupon=coup)

        # 4) Add items with snapshot prices
        p1 = current_price_toman(v1)
        p2 = current_price_toman(v2)
        CartItem.objects.create(cart=cart, variant=v1,
                                qty=2, unit_price_snapshot_toman=p1)
        CartItem.objects.create(cart=cart, variant=v2,
                                qty=1, unit_price_snapshot_toman=p2)

        # 5) Totals (simple demo calc):
        items_subtotal = 2 * p1 + 1 * p2

        # coupon discount — percent of subtotal (no scoping in demo)
        coupon_discount = 0
        if coup.is_active:
            if coup.type == CouponType.PERCENT:
                coupon_discount = (items_subtotal * coup.value) // 100
            else:
                coupon_discount = min(items_subtotal, coup.value)

        # global discount applies AFTER coupon, on the remainder
        remainder = items_subtotal - coupon_discount
        global_off = 0
        if gd.is_active:
            global_off = (remainder * gd.percent_off) // 100

        # shipping fee (demo)
        shipping_fee = 50_000

        payable = max(0, remainder - global_off + shipping_fee)

        # 6) Checkout snapshot
        Checkout.objects.update_or_create(
            cart=cart,
            defaults={
                "status": CheckoutStatus.STARTED,
                "phone_number": "+989121234567",
                "email": None,
                "shipping_address_json": {
                    "full_name": "کاربر مهمان",
                    "line1": "تهران، خیابان ولیعصر، پلاک ۱۲۳",
                    "city": "تهران",
                    "postal_code": "1234567890",
                },
                "delivery_option": "post",
                "payment_method": "zarrinpal",
                "items_subtotal_toman": items_subtotal,
                "discounts_total_toman": coupon_discount,
                "global_discount_toman": global_off,
                "shipping_fee_toman": shipping_fee,
                "payable_toman": payable,
            },
        )

        self.stdout.write(self.style.SUCCESS(
            "✅ Promotions & demo cart/checkout seeded"))
        self.stdout.write(f"Cart ID: {cart.id} (anonymous_id: {anon_id})")
        self.stdout.write(
            f"Subtotal: {items_subtotal:,}  Coupon: {coupon_discount:,}  Global: {global_off:,}  Shipping: {shipping_fee:,}  Payable: {payable:,}")
