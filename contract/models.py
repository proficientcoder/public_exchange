from django.db import models
from django.contrib.auth.models import User


# Create your models here.
legal_forms = (
    (1, 'Deliverable'),
    (2, 'Ownership')
)

class Contract(models.Model):

    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    descriptive_name = models.CharField(max_length=32, unique=True)     # Should add hostname
    legal = models.IntegerField(choices=legal_forms, default=1)
    unique = models.BooleanField(default=True)                          # Can other users produce this as well?
    website = models.CharField(max_length=512, unique=True)
    expiry_date = models.DateTimeField()
    underlying_value = models.TextField()

