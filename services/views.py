from django.shortcuts import render

def home_view(request):
    return render(request, 'services/home.html')

def profile(request):
    return render(request, 'services/profile.html')

def services(request):
    return render(request, 'services/services.html')

def about(request):
    return render(request, 'services/about.html')

def soilInfo(request):
    return render(request, 'services/SoilInfo.html')