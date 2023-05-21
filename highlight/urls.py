from django.urls import path

from . import views
from .views import *

urlpatterns = [
    path("create-highlight", views.create_highlight, name="create-highlight"),
    path("get-result/<str:token>", views.get_result, name="get-result"),
]