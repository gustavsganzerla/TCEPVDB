from django.urls import path
from . import views


app_name = "poxidb"

urlpatterns = [
    path("poxidb/", views.poxidb, name = "poxidb")
    
]
