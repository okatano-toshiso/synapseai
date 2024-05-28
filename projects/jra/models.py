from django.db import models

# Create your models here.
class RaceInfo(models.Model):
    csv_file = models.FileField(upload_to='uploads/jra/')