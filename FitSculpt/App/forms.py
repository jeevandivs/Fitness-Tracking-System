# forms.py
from django import forms
from .models import *
from django.contrib.auth.password_validation import validate_password

class ClientUpdateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['username', 'gender', 'height', 'weight', 'food_type']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter your username', 'class': 'form-control'}),
            'gender': forms.TextInput(attrs={'placeholder': 'Enter your gender(Male , female, or others)', 'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'placeholder': 'Enter your height in Centi Meters', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'placeholder': 'Enter your weight in Kilo Grams', 'class': 'form-control'}),
            'food_type': forms.TextInput(attrs={'placeholder': 'Enter your food type(Enter Veg for vegetarian & Enter Non-Veg for non vegetarian)', 'class': 'form-control'}),
        }

class FmUpdateForm(forms.ModelForm):
    class Meta:
        model =FitnessManager
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Update your username', 'class': 'form-control'}),
            'password': forms.TextInput(attrs={'placeholder': 'Update your password', 'class': 'form-control'}),

        }
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