# forms.py
from django import forms
from .models import *
from django.contrib.auth.password_validation import validate_password

from django import forms
from .models import Client  # Adjust based on your project structure
import re

class ClientUpdateForm(forms.ModelForm):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
    ]

    FOOD_TYPE_CHOICES = [
        ('veg', 'Vegetarian'),
        ('non_veg', 'Non-Vegetarian'),
    ]

    gender = forms.ChoiceField(choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    food_type = forms.ChoiceField(choices=FOOD_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Client
        fields = ['username', 'gender', 'height', 'weight', 'food_type','profile_picture']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username', 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Enter your height in Centimeters', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Enter your weight in Kilograms', 'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),

        }

    def clean_username(self):
        username = self.cleaned_data['username']
        username_regex = r'^[A-Za-z]\w{5,29}$'
        
        # Check if the username follows the required pattern
        if not re.match(username_regex, username):
            raise forms.ValidationError("Username must start with a letter and be between 6 to 30 characters.")
        
        # Check if the username already exists, excluding the current user
        if Client.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")

        return username

    def clean_height(self):
        height = self.cleaned_data['height']
        if height < 60 or height > 230:
            raise forms.ValidationError("Height must be between 60 cm and 230 cm.")
        return height

    def clean_weight(self):
        weight = self.cleaned_data['weight']
        if weight < 20 or weight > 300:
            raise forms.ValidationError("Weight must be between 20 kg and 300 kg.")
        return weight





from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import FitnessManager  # Adjust based on your project structure
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
import re
from .models import FitnessManager, Client  # Adjust based on your project structure

class FmUpdateForm(forms.ModelForm):
    class Meta:
        model = FitnessManager
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Update your username', 'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'placeholder': 'Update your password', 'class': 'form-control'}),
        }
        error_messages = {
            'password': {
                'required': 'Password is required.',
                'min_length': 'Password must be at least 8 characters long.',
                'max_length': 'Password cannot exceed 20 characters.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].validators.extend([
            MinLengthValidator(8, message='Password must be at least 8 characters long.'),
            MaxLengthValidator(20, message='Password cannot exceed 20 characters.'),
        ])

    def clean_username(self):
        username = self.cleaned_data['username']
        username_regex = r'^[A-Za-z]\w{5,29}$'
        
        # Check if the username follows the required pattern
        if not re.match(username_regex, username):
            raise forms.ValidationError("Username must start with a letter and be between 6 to 30 characters.")
        
        # Check if the username already exists, excluding the current user
        if FitnessManager.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken. Please choose a different one.")

        return username




class SetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'password'}),
        label='New Password',
        
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'confirm_password'}),
        label='Confirm New Password'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
class Fm_SetPasswordForm(forms.Form):
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'password'}),
        label='New Password',
        validators=[validate_password]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'confirm_password'}),
        label='Confirm New Password'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        

# forms.py

from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_text']
        widgets = {
            'message_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter your message...'}),
        }
