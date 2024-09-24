# forms.py
from django import forms
from .models import *
from django.contrib.auth.password_validation import validate_password

from django import forms
from .models import Client  # Adjust based on your project structure

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
        fields = ['username', 'gender', 'height', 'weight', 'food_type']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username', 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Enter your height in Centimeters', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Enter your weight in Kilograms', 'class': 'form-control'}),
        }




from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import FitnessManager  # Adjust based on your project structure

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