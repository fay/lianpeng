from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import F

# Create your models here.

class Website(models.Model):
    favicon = models.ImageField(upload_to="favicons")
    domain = models.CharField(max_length=120, unique=True)
