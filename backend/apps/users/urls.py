# apps/users/urls.py

from django.urls import path
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(["GET"])
def test_user(request):
    return Response({"message": "Users endpoint works"})

urlpatterns = [
    path("test/", test_user),
]