from django.db import models


class Announcement(models.Model):
    text = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    style = models.CharField(max_length=20, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
