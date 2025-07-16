from django.urls import path

from . import views # This . package just means "the current package; we are importing the sister file "views.py"

urlpatterns = [
    path("", views.login_view, name="login_view"),
    path("login", views.login_view, name="login_view"),
    path("register", views.register_view, name="register_view"),
]