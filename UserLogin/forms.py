from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, MenuItems
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'name', 'email', 'userType')
        widgets = {
            'userType': forms.RadioSelect(),
            'username': forms.TextInput(attrs={'placeholder': 'Username/Shop Name'}),
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email ID'}),
        }
        labels = {
            'userType': '',
            'username': '',
            'name': '',
            'email': '',
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Password'})
        self.fields['password1'].label = ""
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Password confirmation'})
        self.fields['password2'].label = ""
        print('self fields', self.fields['userType'].widget)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username/Shop Name'}),
        }


class AddMenuItem(forms.ModelForm):
    class Meta:
        model = MenuItems
        fields = ('itemName', 'price')
