from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CouponViewSet, ProductDiscountViewSet

router = DefaultRouter()
router.register(r'coupons', CouponViewSet, basename='coupon')
router.register(r'product-discounts', ProductDiscountViewSet, basename='product-discount')

app_name = 'discount'

urlpatterns = [
    path('', include(router.urls)),
]
