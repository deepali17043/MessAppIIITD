from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, MenuItems
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'name', 'email', 'userType')
        widgets = {
            'userType': forms.RadioSelect()
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields


class AddMenuItem(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = ('itemName', 'price')
