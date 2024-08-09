# App/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
from .models import *
def signup_view(request):
    print("I'm here")
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        phone = int(request.POST.get('phone'))

        print(f"Form Data: {fname}, {lname}, {username}, {password}, {email}, {phone}")

        if password == confirm_password:
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO client (fname, lname, username, password, email, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                        [fname, lname, username, password, email, phone]
                    )
                messages.success(request, 'Account created successfully')
                print("Data Inserted Successfully")
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Error occurred: {e}')
                print(f"Error: {e}")
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'signup.html')

def login_view(request):
    return render(request, 'login.html')

def client_view(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if Client.objects.filter(username=username,password=password).exists():
            userdetails=Client.objects.get(username=request.POST['username'], password=password)
            if userdetails.password == request.POST['password']:
                
                return render(request,'client.html')
        return render(request,'login.html')
    

def home_view(request):
    return render(request, 'home.html')

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')
def home_view(request):
    return render(request, 'home.html')
