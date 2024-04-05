from django.db import models

class DemoImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
