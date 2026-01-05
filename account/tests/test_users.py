import pytest
from rest_framework import status

      
@pytest.mark.django_db
class TestMeView:
    
    def test_me_endpoint_get_200(self, api_client, db_user, me_endpoint):
        api_client.force_authenticate(user=db_user)
        response = me_endpoint["get"]({})
        assert response.status_code == status.HTTP_200_OK
    
    def test_me_endpoint_put_200(self, api_client, db_user, me_endpoint):
        api_client.force_authenticate(user=db_user)
        response = me_endpoint["put"]({"phone": "+201234567890"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("phone") == "+201234567890"
        
    def test_me_endpoint_patch_200(self, api_client, db_user, me_endpoint):
        api_client.force_authenticate(user=db_user)
        response = me_endpoint["patch"]({"phone": "+201234567890"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get("phone") == "+201234567890"    
        
    


@pytest.mark.django_db
class TestUsersStuffList:
    def test_list_users_staff_200(self, api_client, db_user, users_stuff_endpoint):
        # Make user staff
        db_user.role = "staff"
        db_user.save()
        
        api_client.force_authenticate(user=db_user)
        response = users_stuff_endpoint()
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_non_staff_403(self, api_client, db_user, users_stuff_endpoint):
        api_client.force_authenticate(user=db_user)
        response = users_stuff_endpoint()
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_users_unauthenticated_401(self, api_client, users_stuff_endpoint):
        response = users_stuff_endpoint()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED