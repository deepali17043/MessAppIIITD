from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import *
from django import forms
"""
All of the fields as present in the model classes have been defined in detail in models.py
"""


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user in the database.
    """
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
    """
    Form for changing the details of a user.
    """
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username/Shop Name'}),
        }


class AddMenuItem(forms.ModelForm):
    """
    Form for adding menu items to the menu for any stall associated with a vendor.
    Data required:
        itemName - Name of the dish
        price - cost of the item
    """
    class Meta:
        model = MenuItems
        fields = ('itemName', 'price')


class AttendanceList(forms.ModelForm):
    """
    Used while uploading a list of students who showed up in the mess:
        on a given date
        for a given meal
    """
    class Meta:
        model = MessAttendance
        fields = ('meal', 'date')


class AttendeesForm(forms.Form):
    """
    Used for obtaining the list of students who marked their attendance as "attending"
        on a given date
        for a given meal
    """
    date = forms.DateField(label='Date', widget=forms.SelectDateWidget)
    meal = forms.ChoiceField(choices=(('Breakfast', 'Breakfast'),
                                    ('Lunch', 'Lunch'),
                                    ('Snacks', 'Snacks'),
                                    ('Dinner', 'Dinner')))


class DefaultDeadlineForm(forms.ModelForm):
    """
    Form for editing the default deadline for a meal
    """
    class Meta:
        model = DefaultDeadline
        fields = ('meal', 'hours')


class MealDeadlineForm(forms.ModelForm):
    """
    For Announcement of a special deadline, that won't be followed everyday
    """
    class Meta:
        model = MealDeadline
        fields = ('date', 'meal', 'hours')


class DefaultMessMenuForm(forms.ModelForm):
    """
    Form for editing the weekly mess menu
    """
    class Meta:
        model = DefaultMessMenu
        fields = ('day', 'meal', 'items', 'special_menu', 'contains_egg', 'contains_chicken')
        widegets = {
            'day': forms.TextInput(attrs={'disabled': True}),
            'meal': forms.TextInput(attrs={'disabled': True})
        }


class MessMenuForm(forms.ModelForm):
    """
    Form for adding a special menu to the mess menu
    attributing the special meal to an occasion is allowed
    """
    class Meta:
        model = MessMenu
        fields = ('date', 'meal', 'items', 'occasion')
        widgets = {
            'date': forms.SelectDateWidget()
        }


class MessMenuSearchForm(forms.Form):
    """
    Search for the special mess menu according to date.
    """
    date = forms.DateField(label='Date ', widget=forms.SelectDateWidget)
