from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=6)
    
    required_service_hours = models.FloatField(default=20.0)  
    completed_service_hours = models.FloatField(default=0.0)
    penalty_service_hours = models.FloatField(default=0.0)

class OrgProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class OAAProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
