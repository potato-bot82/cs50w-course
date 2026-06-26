from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse

from .models import User, FAQ

# Create your views here.
def index(request):
   return render(request, "chatbot/index.html")

def chatbot_response(request):
    user_question = request.GET.get("question", "").lower()
    faq = FAQ.objects.filter(question__icontains=user_question).first()
    
    if faq:
        return JsonResponse({"answer": faq.answer})
    else:
        return JsonResponse({"answer": "Maaf, aku tidak tahu jawabannya. Coba pertanyaan lain!"})

def rasa_chat(request):
    user_message = request.GET.get("question", "")
    if not user_message:
        return JsonResponse({"answer": "Silakan masukkan pertanyaan!"})

    rasa_url = "http://localhost:5005/webhooks/rest/webhook"  # URL Rasa API
    payload = {"sender": "user", "message": user_message}

    try:
        response = request.post(rasa_url, json=payload)
        response_data = response.json()

        if response_data:
            bot_reply = response_data[0].get("text", "Maaf, saya tidak mengerti.")
        else:
            bot_reply = "Maaf, tidak ada respons dari chatbot."

        return JsonResponse({"answer": bot_reply})
    except request.exceptions.RequestException:
        return JsonResponse({"answer": "Gagal terhubung ke chatbot Rasa!"})
    
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "chatbot/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "chatbot/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "chatbot/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "chatbot/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "chatbot/register.html")