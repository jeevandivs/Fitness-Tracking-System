from datetime import datetime
from urllib import request
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import connection
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ClientUpdateForm # type: ignore
from .models import Client
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from FitSculpt import settings
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views.decorators.cache import never_cache
from .decorators import custom_login_required

def index_view(request):
    return render(request, 'index.html')

def calculate_age(dob):
    today = datetime.today().date()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email address')
            return render(request, 'register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')

        if username in ['fm001', 'admin001']:
            messages.error(request, 'This username cannot be taken.')
            return render(request, 'register.html')

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM client WHERE username = %s", [username])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Username already exists')
                    return render(request, 'register.html')

                cursor.execute("SELECT COUNT(*) FROM client WHERE email = %s", [email])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Email already registered')
                    return render(request, 'register.html')

                cursor.execute("SELECT COUNT(*) FROM client WHERE phone = %s", [phone])
                if cursor.fetchone()[0] > 0:
                    messages.error(request, 'Phone number already registered')
                    return render(request, 'register.html')
        except Exception as e:
            messages.error(request, f'Error checking username, email, or phone: {e}')
            return render(request, 'register.html')

        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d').date()
            if dob_date > datetime.today().date():
                messages.error(request, 'Date of birth cannot be in the future.')
                return render(request, 'register.html')
            age = calculate_age(dob_date)
        except ValueError:
            messages.error(request, 'Invalid date format. Use YYYY-MM-DD.')
            return render(request, 'register.html')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO client (name, email, phone, dob, username, password, age, date_joined) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
                    [name, email, phone, dob_date, username, password, age]
                )
            messages.success(request, 'Account created successfully')
            return redirect('login')  
        except Exception as e:
            messages.error(request, f'Error occurred: {e}')
            return render(request, 'register.html')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = Client.objects.get(username=username)
            if user.password == password:  
                request.session['user_id'] = user.user_id 
                request.session['username'] = user.username  
                return redirect('user_home')  
            else:
                messages.error(request, 'Invalid username or password.')
        except Client.DoesNotExist:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def google_login_view(request):
    return render(request, 'google_login.html')

def forgot_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        try:
            user = Client.objects.get(username=username, email=email)
            send_mail( 
                'Your Password Recovery',
                f'Hello {user.name}, your password is: {user.password}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Your password has been sent to your email.')
            return render(request,'login.html')
        except Client.DoesNotExist:
            messages.error(request, 'Invalid username or email.')
        
    return render(request, 'forgot.html')
def fm_home_view(request):
    return render(request, 'login.html')

def fm_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'fm001' and password == 'fm001':
            return render(request, 'fm_home.html')
    return render(request, 'fm_login.html')

@custom_login_required
def user_home_view(request):
    return render(request, 'user_home.html')
@custom_login_required
def user_profile_view(request):
    user_id = request.session.get('user_id')  

    if user_id:
        client = Client.objects.get(user_id=user_id)  
        
        if request.method == 'POST':
            form = ClientUpdateForm(request.POST, instance=client)
            if form.is_valid():
                form.save()
                return redirect('user_home')
        else:
            form = ClientUpdateForm(instance=client)
        
        return render(request, 'user_profile.html', {'form': form, 'client': client})
    return redirect('login')

@custom_login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin001' and password == 'admin001':
            return render(request, 'admin_home.html')
    return render(request, 'admin_login.html')

def admin_home_view(request):
    return render(request, 'admin_home.html')

