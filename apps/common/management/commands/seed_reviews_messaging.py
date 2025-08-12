from uuid import uuid4
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.catalog.models import Product, ProductVariant, MediaAsset
from apps.orders.models import OrderHeader, OrderLine, CouponRedemption
from apps.reviews.models import Review, ReviewMedia, Wishlist, ReviewStatus
from apps.messaging.models import Campaign, MessageOutbox, ShortLink, ShortLinkClick, MessageStatus


class Command(BaseCommand):
    help = "Seeds demo data for Reviews, Wishlist, Messaging (campaigns, SMS outbox), and ShortLinks."

    def handle(self, *args, **opts):
        # --- sanity checks
        if Product.objects.count() == 0 or ProductVariant.objects.count() == 0:
            self.stdout.write(self.style.WARNING(
                "⚠️ No products/variants found. Run `seed_demo` first."))
            return

        # pick/create a user (use your first superuser if present)
        user = User.objects.order_by("date_joined").first()
        if not user:
            self.stdout.write(self.style.WARNING(
                "⚠️ No users found. Create a superuser first (`createsuperuser`)."))
            return

        # get latest order; if none, ask to run the previous seed
        order = OrderHeader.objects.order_by("-placed_at").first()
        if not order:
            self.stdout.write(self.style.WARNING(
                "⚠️ No orders found. Run `seed_promos_carts` then `seed_order_from_checkout`."))
            return

        # attach order to this user for a clean verified-purchase demo
        if order.user is None:
            order.user = user
            order.save(update_fields=["user"])

        # pick 1–2 products from the order lines (fallback to catalog if needed)
        olines = list(order.lines.select_related("variant__product"))
        products = [ol.variant.product for ol in olines] or list(
            Product.objects.all()[:2])
        products = products[:2]

        # --- Reviews (verified by tying to this order)
        Review.objects.get_or_create(
            product=products[0],
            user=order.user,
            order=order,
            defaults=dict(
                rating=5,
                title="خیلی باکیفیت",
                content="عطر عالی، اسیدیته دلنشین. برای V60 فوق‌العاده بود.",
                status=ReviewStatus.APPROVED,
            ),
        )

        if len(products) > 1:
            r2, _ = Review.objects.get_or_create(
                product=products[1],
                user=order.user,
                order=order,
                defaults=dict(
                    rating=4,
                    title="انتخاب خوب برای اسپرسو",
                    content="بدنه متوسط رو به سنگین، کرما خوب.",
                    status=ReviewStatus.APPROVED,
                ),
            )
            # attach an existing media asset if there is any
            media = MediaAsset.objects.first()
            if media:
                ReviewMedia.objects.get_or_create(review=r2, media=media)

        # --- Wishlist (add 2 variants)
        variants = list(ProductVariant.objects.select_related(
            "product").order_by("created_at")[:2])
        for v in variants:
            Wishlist.objects.get_or_create(user=user, variant=v)

        # --- Messaging & ShortLinks
        camp, _ = Campaign.objects.get_or_create(
            name="Demo Shipping Update",
            defaults=dict(
                channel="sms", template="سفارش شما ارسال شد. پیگیری: {{link}}", variant="A", is_transactional=True),
        )

        # create a short link that points to one product page (fake URL)
        target_slug = products[0].slug_en
        short, _ = ShortLink.objects.get_or_create(
            target_url=f"https://example.com/p/{target_slug}",
            campaign=camp,
            defaults=dict(variant="A"),
        )

        # 1) message to the user
        phone = str(order.user.phone_number) if getattr(
            order.user, "phone_number", None) else "+989121234567"
        msg_user, _ = MessageOutbox.objects.get_or_create(
            campaign=camp,
            user=order.user,
            phone_e164=phone,
            defaults=dict(
                body=f"مرسوله شما ثبت شد. رهگیری: https://example.com/t/{short.uuid_code}",
                status=MessageStatus.SENT,
                shortlink=short,
                sent_at=timezone.now(),
            ),
        )

        # 2) message to a guest number
        msg_guest, _ = MessageOutbox.objects.get_or_create(
            campaign=camp,
            user=None,
            phone_e164="+989000000000",
            defaults=dict(
                body=f"سفارش شما آماده ارسال است: https://example.com/t/{short.uuid_code}",
                status=MessageStatus.DELIVERED,
                shortlink=short,
                sent_at=timezone.now(),
                delivered_at=timezone.now(),
            ),
        )

        # record a click from an anonymous visitor
        ShortLinkClick.objects.get_or_create(
            shortlink=short,
            user=None,
            anonymous_id=uuid4(),
            defaults=dict(utm_json={
                          "utm_source": "sms", "utm_campaign": "demo"}, ip="127.0.0.1", user_agent="SeedBot/1.0"),
        )

        self.stdout.write(self.style.SUCCESS(
            "✅ Seeded reviews, wishlist, campaign/messages, and shortlink + click."))
        self.stdout.write(f"User: {user.phone_number}  |  Order: {order.id}")
