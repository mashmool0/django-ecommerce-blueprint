from django.urls import path
from .views import ZarrinpalCreatePaymentView, ZarrinpalVerifyPaymentView

urlpatterns = [
    path("zarrinpal/create/", ZarrinpalCreatePaymentView.as_view(),
         name="zarrinpal-create"),
    path("zarrinpal/verify/", ZarrinpalVerifyPaymentView.as_view(),
         name="zarrinpal-verify"),
]
