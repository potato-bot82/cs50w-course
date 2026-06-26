from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    # Tambahkan related_name unik untuk menghindari konflik dengan auth.User
    groups = models.ManyToManyField(Group, related_name="chatbot_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="chatbot_user_permissions", blank=True)

    def __str__(self):
        return self.username


class FAQ(models.Model):
    question = models.CharField(max_length=255, unique=True)
    answer = models.TextField()

    def __str__(self):
        return self.question
