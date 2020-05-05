from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django import forms


# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, username, name, email, type, password=None):
        if not username:
            raise ValueError('Username must be set!')
        user = self.model(username=username, name=name, authenticated=1, email=self.normalize_email(email))
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
        user.userType = 0
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(username=username)


class User(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True) # vendors will enter their shopname as username.
    userType = models.CharField(max_length=20, choices=(('customer', 'Customer'), ('vendor', 'Vendor')), default='customer')
    email = models.EmailField()
    name = models.CharField(max_length=255)
    authenticated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    # this field is required to login super user from admin panel
    is_staff = models.BooleanField(default=True)
    # this field is required to login super user from admin panel
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def authenticateUser(self):
        self.authenticated = True;
        self.save()

    def deAuthenticateUser(self):
        self.authenticated = False
        self.save()

    def isAuthenticated(self):
        return self.authenticated


class MenuItems(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')
    price = models.IntegerField(default=0)
    itemName = models.CharField(max_length=255)
    hidden = models.BooleanField(default=False)


class Cart(models.Model):
    item = models.ForeignKey(MenuItems, on_delete=models.CASCADE, related_name='item')
    qty = models.PositiveSmallIntegerField(default=1)
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='user')
    orderPlaced = models.PositiveSmallIntegerField(default=0, choices=((0, 0), (1, 1), (2, 2)))
    status = models.CharField(max_length=50,
                              choices=(('Added to Cart', 'Added to Cart'),
                                       ('Order Placed', 'Order Placed'),
                                       ('Being Prepared', 'Being Prepared'),
                                       ('Prepared', 'Prepared'),
                                       ('Collected', 'Collected')),
                              default='Added to Cart')
