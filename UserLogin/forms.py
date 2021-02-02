from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django import forms


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'name', 'email', 'type')
        widgets = {
            'type': forms.RadioSelect(),
            'username': forms.TextInput(attrs={'placeholder': 'Username/Shop Name'}),
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'email': forms.TextInput(attrs={'placeholder': 'Email ID'}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Password'})
        self.fields['password1'].label = ""
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control',
                                                                     'placeholder': 'Password confirmation'})
        self.fields['password2'].label = ""
        print('self fields', self.fields['type'].widget)


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


class AttendanceList(forms.ModelForm):
    class Meta:
        model = MessAttendance
        fields = ('meal', 'date')


class AttendeesForm(forms.Form):
    date = forms.DateField(label='Date', widget=forms.SelectDateWidget)
    meal = forms.ChoiceField(choices=(('Breakfast', 'Breakfast'),
                                    ('Lunch', 'Lunch'),
                                    ('Snacks', 'Snacks'),
                                    ('Dinner', 'Dinner')))


class DefaultDeadlineForm(forms.ModelForm):
    class Meta:
        model = DefaultDeadline
        fields = ('meal', 'hours')


class MealDeadlineForm(forms.ModelForm):
    class Meta:
        model = MealDeadline
        fields = ('date', 'meal', 'hours')
