from django.urls import path
from . import views


app_name = "poxidb"

urlpatterns = [
    path("poxidb/", views.poxidb, name = "poxidb"),
    path("visualize_proteome/<str:organism>", views.visualize_proteome, name = "visualize_proteome"),
    path("download_proteome/<str:organism>", views.download_proteome, name = "download_proteome"),
    path("visualize_antigens/<str:organism>", views.visualize_antigens, name = "visualize_antigens"),
    path("download_antigens/<str:organism>", views.download_proteome, name = "download_antigens"),
    path("visualize_individual_epitopes/<path:description>", views.visualize_individual_epitopes, name = "visualize_individual_epitopes"),
    path("download_individual_epitopes/<path:description>", views.download_individual_epitopes, name = "download_individual_epitopes"),
    path("visualize_epitopes/<str:organism>", views.visualize_epitopes, name = "visualize_epitopes"),
    path("download_epitopes/<str:organism>", views.download_epitopes, name = "download_epitopes")
]
