from django.db import models

# Create your models here.
class Files(models.Model):
    """ upload files"""
    file = models.FileField(upload_to='uploads/')

    class Meta:
        ordering = ['-id']