from django.db import models
from django.contrib.auth.models import User


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=6, unique=True)

    required_service_hours = models.FloatField(default=20.0)
    completed_service_hours = models.FloatField(default=0.0)
    penalty_service_hours = models.FloatField(default=0.0)


class OrgProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class OAAProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Event(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=50)
    service_hours = models.IntegerField()
    number_of_students = models.IntegerField()
    role_descriptions = models.TextField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    organizer = models.ForeignKey(
        OrgProfile, on_delete=models.CASCADE, related_name="events"
    )
    approved = models.BooleanField(default=False)
    students = models.ManyToManyField(
        StudentProfile, through="Participation", related_name="events"
    )

    def remaining_slots(self):
        assigned_count = self.participation_set.count()
        return max(0, self.number_of_students - assigned_count)

    def is_user_in_event(self, user):
        try:
            student_profile = user.studentprofile
        except StudentProfile.DoesNotExist:
            return False

        return Participation.objects.filter(student=student_profile, event=self).exists()


class Participation(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
