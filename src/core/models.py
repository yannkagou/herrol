from django.db import models
# from django.contrib.auth.models import User

class ImportedFile(models.Model):
    file = models.FileField(upload_to='uploaded_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Report(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='reports/images/', null=True, blank=True, default='default_image.png')
    image_par_heure = models.ImageField(upload_to='reports/images/', null=True, blank=True, default='default_image_par_heure.png')
    file = models.FileField(upload_to='reports/files/')
