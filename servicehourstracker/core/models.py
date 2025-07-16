from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=6)

class OrgProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class OAAProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
