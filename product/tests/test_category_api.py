import pytest
from django.urls import reverse
from rest_framework import status
from product.models.category import Category

@pytest.mark.django_db
class TestCategoryAPI:
    def test_list_categories(self, api_client):
        Category.objects.create(name="Electronics", slug="electronics")
        Category.objects.create(name="Fashion", slug="fashion")
        
        url = reverse("product:category-list")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_category_as_admin(self, api_client):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.create(email="admin@test.com", is_staff=True, role="staff")
        api_client.force_authenticate(user=admin_user)
        
        url = reverse("product:category-list")
        data = {"name": "Home & Garden", "slug": "home-garden"}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name="Home & Garden").exists()

    def test_create_category_as_anonymous_fails(self, api_client):
        url = reverse("product:category-list")
        data = {"name": "Illegal Category", "slug": "illegal"}
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_category(self, api_client):
        category = Category.objects.create(name="Toys", slug="toys")
        url = reverse("product:category-detail", kwargs={"pk": category.pk})
        
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Toys"
