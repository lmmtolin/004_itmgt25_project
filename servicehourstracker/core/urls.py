from django.urls import path

from . import views # This . package just means "the current package; we are importing the sister file "views.py"

urlpatterns = [
    path("", views.login_view, name="login_view"),
    path("login", views.login_view, name="login_view"),
    path("register", views.register_view, name="register_view"),
    path("student_dashboard", views.student_dashboard, name="student_dashboard"),
    path("org_dashboard", views.org_dashboard, name="org_dashboard"),
    path("oaa_dashboard", views.oaa_dashboard, name="oaa_dashboard"),
]