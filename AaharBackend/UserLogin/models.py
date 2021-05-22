from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import datetime

# Required for declaring types of meals possible in Models related to Mess
meal_choices = (
    ('Breakfast', 'Breakfast'),
    ('Lunch', 'Lunch'),
    ('Snacks', 'Snacks'),
    ('Dinner', 'Dinner')
)

# Required for declaring values of days possible in Models related to Mess Menu
day_choices = (
    ('Monday', 'Monday'),
    ('Tuesday', 'Tuesday'),
    ('Wednesday', 'Wednesday'),
    ('Thursday', 'Thursday'),
    ('Friday', 'Friday'),
    ('Saturday', 'Saturday'),
    ('Sunday', 'Sunday'),
)


class UserManager(BaseUserManager):
    def create_user(self, username, name, email, type, password=None):
        if not username:
            raise ValueError('Username must be set!')
        user = self.model(username=username, name=name, type=type, email=self.normalize_email(email))
        user.is_admin = False
        user.is_staff = False
        user.is_superuser = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        print("email: ")
        email = input()
        user = self.create_user(username, username, email, password)
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(username=username)


class User(AbstractBaseUser):
    """
    Model corresponding to any user's data on our database.
    Caters to All types: customer, admin, vendor and mess vendor

    Stores:
        username
        type
        email
        name
    and other information necessary for AbstractBaseUser
    """
    username = models.CharField(max_length=255, unique=True)  # vendors will enter their shopname as username.
    type = models.CharField(max_length=20,
                            choices=(('customer', 'Customer'),
                                     ('vendor', 'Vendor'),
                                     ('admin', 'Admin'),
                                     ('mess-vendor', 'Mess Vendor')),
                            default='customer')
    email = models.EmailField()
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    # this field is required to login super user from admin panel
    is_staff = models.BooleanField(default=True)
    # this field is required to login super user from admin panel
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'


class MenuItems(models.Model):
    """
    Corresponds to the Menu of a particular vendor (Canteen, Tea shop etc),
    Stores:
        vendor - Foreign Key (from table/collection of Users)
        price
        item name
        hidden
    """
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')
    price = models.IntegerField(default=0)
    itemName = models.CharField(max_length=255)
    hidden = models.BooleanField(default=False)
    # is_hidden = models.PositiveSmallIntegerField(choices=((0, 0), (1, 1)), default=0)


class Cart(models.Model):
    """
    Corresponding to the items in a user's cart
        item - Foreign Key (From table/collection of MenuItems)
        customer - Foreign Key (From table/collection of Users (type customer))
        qty - small integer for quantity of the item to be purchased
        orderPlaced - whether or not the order has been placed
        orderTime - time at which the order was placed
        status - status of the order
    """
    item = models.ForeignKey(MenuItems, on_delete=models.CASCADE, related_name='item')
    qty = models.PositiveSmallIntegerField(default=1)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user')
    orderPlaced = models.PositiveSmallIntegerField(default=0, choices=((0, 0), (1, 1), (2, 2)))
    orderTime = models.DateTimeField(default=datetime.datetime.now, blank=True)
    status = models.CharField(max_length=50,
                              choices=(('Added to Cart', 'Added to Cart'),
                                       ('Order Placed', 'Order Placed'),
                                       ('Being Prepared', 'Being Prepared'),
                                       ('Prepared', 'Prepared'),
                                       ('Collected', 'Collected')),
                              default='Added to Cart')


class MessUser(models.Model):
    """
    Model for Mess Users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, null=False, db_index=True)
    breakfast_coupons = models.PositiveSmallIntegerField(default=20)
    lunch_coupons = models.PositiveSmallIntegerField(default=20)
    snacks_coupons = models.PositiveSmallIntegerField(default=20)
    dinner_coupons = models.PositiveSmallIntegerField(default=20)


class MessAttendance(models.Model):
    """
    Model for Attendance Objects
    Default value of marked attendance has to be False
        user - Foreign Key (From Users table/Collection)
        meal - Attendance for the meal specified by this object
        date - Attendance for the meal on the date specified by this field.
        attending - marked attendance value (True/False)
        attended - physical attendance as uploaded by the Admin (True/False)
        defaulter - True if the attending value and attended value don't match, False otherwise
        editable - False if the deadline for the meal on the given date is no longer editable, True otherwise
    """
    user = models.ForeignKey(MessUser, on_delete=models.CASCADE, related_name='mess_customer')
    meal = models.CharField(max_length=10, choices=meal_choices)
    attending = models.BooleanField(default=False)
    # is_attending = models.PositiveSmallIntegerField(choices=((0, 0), (1, 1)), default=0)
    date = models.DateField(default=datetime.date.today())
    attended = models.BooleanField(default=False)
    # has_attended = models.PositiveSmallIntegerField(choices=((0, 0), (1, 1)), default=0)
    defaulter = models.BooleanField(default=False)
    # is_defaulter = models.PositiveSmallIntegerField(choices=((0, 0), (1, 1)), default=0)
    editable = models.BooleanField(default=True)
    # is_editable = models.PositiveSmallIntegerField(choices=((0, 0), (1, 1)), default=0)


# Mess Feedback
class Feedback(models.Model):
    """
    Model for storing feedback received for mess
        user: Foreign Key (from Collection User)
        meal: Feedback corresponding to specified meal
        date: Feedback corresponding to specified meal and specified date
        feedback: The feedback text
        status: If the feedback has been sent/approved or needs further discussion
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usr_feedback')
    meal = models.CharField(max_length=10, choices=meal_choices)
    date = models.DateField(default=datetime.date.today())
    feedback = models.TextField()
    status = models.CharField(max_length=10, choices=(('sent', 'Sent'),
                                                      ('approved', 'Approved'),
                                                      ('check mail', 'check mail')), default='sent')


class MealDeadline(models.Model):
    """
    Model to declare any special deadlines - applicable only for the specified date and meal
        date: Entry corresponding to date specified by this field
        meal: Entry corresponding to meal specified by this field
        hours: (int) Number of hours before the meal crossing which attendance is not editable
    """
    date = models.DateField(default=datetime.date.today())
    meal = models.CharField(max_length=10, choices=meal_choices)
    hours = models.PositiveSmallIntegerField(default=6)


class DefaultDeadline(models.Model):
    """
    Model to store Default deadlines per meal.
    """
    meal = models.CharField(max_length=10, unique=True, choices=meal_choices)
    hours = models.PositiveSmallIntegerField(default=6)


class DefaultMessMenu(models.Model):
    """
    Model to store Weekly Menu
        id: Primary Key (django database library did not create primary key by default)
        meal: Entry corresponds to meal defined by this field
        day: entry corresponds to menu on weekday specified by this field
        items: List of Mess Menu items
        special_menu: (True/False) True if the menu contains special items like Paneer etc. False otherwise
        contains_egg: (True/False) True if the menu items contain egg, False otherwise
        contains_chicken: (True/False) True if the menu items contain chicken, False otherwise
    """
    id = models.AutoField(primary_key=True)
    meal = models.CharField(max_length=10, choices=meal_choices)
    day = models.TextField(max_length=15, choices=day_choices)
    items = models.TextField(max_length=400)
    special_menu = models.BooleanField(default=False)
    contains_egg = models.BooleanField(default=False)
    contains_chicken = models.BooleanField(default=False)


class MessMenu(models.Model):
    """
    Model corresponding to special mess menu (in case of an occasion)
        items: Menu Items list
        date: Date corresponding to the special mess menu
        occasion: To specify the occasion
        meal: Breakfast, Lunch, snacks or Dinner
    """
    items = models.TextField(max_length=400)
    date = models.DateField()
    occasion = models.TextField(default='-')
    meal = models.CharField(max_length=10, choices=meal_choices)


class AppFeedback(models.Model):
    """
    Model to store and handle on App Feedback
        user: Foreign Key (from User Table/Collection)
        feedback: feedback text.
        timestamp: time of sending the feedback
        status: To store if the feedback is being processed/resolved.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_app_feedback')
    feedback = models.TextField(max_length=500)
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=10,
                              choices=(('Sent', 'Sent'), ('Resolved', 'Resolved')),
                              default='Sent')
