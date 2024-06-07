from django.db import models
from django.contrib.auth.models import User

class Blogpost(models.Model):
    title = models.CharField(max_length=64)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    edited = models.BooleanField(default=False)
    last_edit = models.DateTimeField(null=True, blank=True)
