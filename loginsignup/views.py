from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# REGISTER VIEW

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        email = request.POST.get("email").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validation
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('loginsignup:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('loginsignup:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('loginsignup:register')

        # Create user
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! Please login.")
        return redirect('loginsignup:login')

    return render(request, "loginsignup/register.html")



# LOGIN VIEW

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username").strip()
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')  # Redirect to home page
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('loginsignup:login')

    return render(request, "loginsignup/login.html")



# LOGOUT VIEW

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')
