from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    text = models.CharField(max_length=240)
    date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE, # When we delete the user it will also delete their posts
    )

    def __str__(self):
        return self.text[0:100] # Truncating the first 100 characters
    
