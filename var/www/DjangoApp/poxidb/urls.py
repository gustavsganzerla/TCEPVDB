from django.urls import path
from . import views


app_name = "poxidb"

urlpatterns = [
    path("poxidb_all/", views.poxidb_all, name = "poxidb_all"),
    path("poxidb_home/", views.poxidb_home, name = "poxidb_home"),
    path("visualize_proteome/<str:organism>", views.visualize_proteome, name = "visualize_proteome"),
    path("download_proteome/<str:organism>", views.download_proteome, name = "download_proteome"),
    path("visualize_antigens/<str:query>", views.visualize_antigens, name = "visualize_antigens"),
    path("download_antigens/<str:query>", views.download_antigens, name = "download_antigens"),
    path("visualize_individual_epitopes/<path:description>", views.visualize_individual_epitopes, name = "visualize_individual_epitopes"),
    path("download_individual_epitopes/<path:description>", views.download_individual_epitopes, name = "download_individual_epitopes"),
    path("visualize_epitopes/<str:query>", views.visualize_epitopes, name = "visualize_epitopes"),
    path("download_epitopes/<str:query>", views.download_epitopes, name = "download_epitopes"),
    path("funding/", views.funding, name = "funding")
]
