from django.db import models

# Create your models here.
class Files(models.Model):
    """ File upload """
    file = models.FileField(upload_to='uploads/')

    class Meta:
        ordering = ['-id']