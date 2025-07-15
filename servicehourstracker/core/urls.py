from django.urls import path

from . import views # This . package just means "the current package; we are importing the sister file "views.py"

urlpatterns = [
    path("", views.index, name="index")
]