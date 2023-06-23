from django.db import models


class Video(models.Model):
    link = models.CharField(max_length=255)
    output_format = models.CharField(max_length=20)
    progress = models.IntegerField(default=0)
