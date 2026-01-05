import pytest
from django.urls import reverse
from rest_framework import status
from account.models import SellerProfile
from store.models import Store
from product.models import Product
from order.models import Order, OrderItem
from decimal import Decimal

@pytest.fixture
def analytics_seller(db_user):
    profile, _ = SellerProfile.objects.get_or_create(user=db_user)
    profile.onboarding_completed = True
    profile.is_verified = True
    profile.save()
    Store.objects.create(seller=profile, name="Data Store", is_approved=True)
    return db_user

@pytest.mark.django_db
class TestAnalyticsAPI:
    
    def test_seller_dashboard_summary(self, api_client, analytics_seller, customer_user):
        store = Store.objects.get(seller__user=analytics_seller)
        
        # Create a product
        product = Product.objects.create(
            store=store, name="Widget", price=50.00, stock_quantity=10, is_approved=True
        )
        
        # Create an order
        order = Order.objects.create(user=customer_user, total_amount=100.00)
        OrderItem.objects.create(
            order=order, product=product, quantity=2, price=50.00, store=store
        )
        
        api_client.force_authenticate(user=analytics_seller)
        url = reverse("analytics:analytics-seller-dashboard")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert float(response.data["total_revenue"]) == 100.00
        assert response.data["total_orders"] == 1
        assert response.data["total_products"] == 1
        assert len(response.data["daily_sales"]) == 7

    def test_low_stock_alerts(self, api_client, analytics_seller):
        store = Store.objects.get(seller__user=analytics_seller)
        Product.objects.create(
            store=store, name="Empty Item", price=10.00, stock_quantity=2, is_approved=True
        )
        
        api_client.force_authenticate(user=analytics_seller)
        url = reverse("analytics:analytics-seller-dashboard")
        response = api_client.get(url)
        
        assert len(response.data["low_stock_alerts"]) == 1
        assert response.data["low_stock_alerts"][0]["name"] == "Empty Item"
