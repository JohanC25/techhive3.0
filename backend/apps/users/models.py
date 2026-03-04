# apps/users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

##class User(AbstractUser):

    ##username = None  # remove default username

    ##ROLE_CHOICES = (
        ##('admin', 'Admin'),
        ##('employee', 'Employee'),
        ##('client', 'Client'),
    ##)

    ##cedula_ruc = models.CharField(
        ##max_length=20,
        ##unique=True
    ##)

    ##full_name = models.CharField(max_length=255)

    ##mobile_phone = models.CharField(max_length=20)
    ##landline_phone = models.CharField(max_length=20, blank=True)

    ##address = models.TextField()

    ##email = models.EmailField(
        ##blank=True,
        ##null=True,
        ##unique=False
    ##)

    ##role = models.CharField(
        ##max_length=20,
        ##choices=ROLE_CHOICES,
        ##default='client'
    ##)

    ##USERNAME_FIELD = 'cedula_ruc'
    ##REQUIRED_FIELDS = ['full_name', 'mobile_phone', 'address']

    ##def __str__(self):
        ##return f"{self.full_name} ({self.role})"