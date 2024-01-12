from django.urls import path
from . import views


app_name = "poxidb"

urlpatterns = [
    path("test_view/", views.test_view, name = "test_view")
    
]
