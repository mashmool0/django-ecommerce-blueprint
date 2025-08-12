from django.utils import timezone
from django.db import models
from apps.orders.models import OrderHeader, OrderLine, OrderStatus
from apps.carts.models import Checkout, CartItem


def create_order_from_checkout(checkout: Checkout, gateway_fee_toman: int = 0) -> OrderHeader:
    """
    Idempotent-ish converter (simple): creates an Order from a Checkout and its CartItems.
    If the checkout already has an order, returns it.
    """
    if hasattr(checkout, "order") and checkout.order:
        return checkout.order

    cart = checkout.cart
    items = CartItem.objects.filter(cart=cart).select_related(
        "variant", "variant__product", "variant__weight_grams")

    # naive order number generation
    next_no = (OrderHeader.objects.aggregate(
        m=models.Max("order_number"))["m"] or 1000) + 1

    order = OrderHeader.objects.create(
        order_number=next_no,
        user=cart.user,
        phone_e164=str(checkout.phone_number),
        email=checkout.email,
        shipping_address_json=checkout.shipping_address_json,
        status=OrderStatus.PAID,  # set PAID after gateway verification
        subtotal_toman=checkout.items_subtotal_toman,
        discounts_toman=checkout.discounts_total_toman,
        global_discount_toman=checkout.global_discount_toman,
        shipping_fee_toman=checkout.shipping_fee_toman,
        total_payable_toman=checkout.payable_toman,
        cogs_total_toman=0,  # TODO: sum your real COGS
        contribution_margin_toman=checkout.payable_toman - 0,
        paid_at=timezone.now(),
        checkout=checkout,
    )

    for it in items:
        OrderLine.objects.create(
            order=order,
            variant=it.variant,
            product_name_fa_snapshot=it.variant.product.name_fa,
            variant_attrs_snapshot={
                "weight_g": it.variant.weight_grams.grams if it.variant.weight_grams_id else None,
                "grind": it.variant.grind_type,
            },
            qty=it.qty,
            unit_price_toman=it.unit_price_snapshot_toman,
            line_discount_toman=it.line_discount_toman,
            unit_cogs_toman=0,  # TODO
            unit_weight_g=it.variant.weight_grams.grams if it.variant.weight_grams_id else None,
        )

    return order
