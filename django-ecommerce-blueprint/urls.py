from django.contrib import admin
admin.site.site_header = "Django E-Commerce Blueprint"
admin.site.site_title = "E-Commerce Blueprint Admin"
admin.site.index_title = "Welcome"


from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
]
