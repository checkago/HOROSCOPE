from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("o-podkhode/", views.about_view, name="about"),
    path("api/options/", views.options_api, name="options_api"),
    path("api/relationship-targets/", views.relationship_targets_api, name="relationship_targets_api"),
    path("api/result/", views.result_api, name="result_api"),
]
