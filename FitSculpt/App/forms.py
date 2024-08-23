# forms.py
from django import forms
from .models import Client

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
