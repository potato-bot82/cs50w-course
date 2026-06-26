from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('chat/', views.chatbot_response, name='chatbot_response'),
    
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # path('chat/', views.rasa_chat, name='rasa_chat'),
]

