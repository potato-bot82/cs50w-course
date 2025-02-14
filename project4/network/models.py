from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Link post a user
    content = models.TextField() #Store post content
    timestamp = models.DateTimeField(auto_now_add=True) #Auto-generate timestamp
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}" #show first 50 chars in admin panel
    
    def total_likes(self):
        return self.likes.count()

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"
