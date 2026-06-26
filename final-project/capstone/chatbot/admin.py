from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import FAQ

# Register FAQ model
admin.site.register(FAQ)
