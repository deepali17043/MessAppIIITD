from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework.settings import api_settings
from rest_framework.validators import UniqueTogetherValidator
from .models import *


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=255)  # vendors will enter their shopname as username.
    type = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)

    def update(self, instance, validated_data):
        """
        Updates and returns the given instance of 'User' with validated_data
        :param instance: Instance to be updated
        :param validated_data: updated information
        :return: modified instance
        """
        # if validated data is available, substitute, otherwise let it be.
        instance.username = validated_data.get('username', instance.username)
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Create and return a new 'User' instance, given the validated data.
        :param validated_data: User object.
        :return: User serialized object
        """
        # print('umm')
        return User.objects.create_user(validated_data.get('username'), validated_data.get('name'),
                                        validated_data.get('email'), validated_data.get('type'))


class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        username = data.get("username", None)

        password = data.get("password", None)
        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password is not found.'
            )
        try:
            # print(user)
            # payload = api_settings.JWT_PAYLOAD_HANDLER(user)
            # jwt_token = api_settings.JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'User with given username and password does not exists'
            )
        return {
            'username': user,
            'password': password
        }

    def create(self, validated_data):
        return SignInSerializer(**validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    validate_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'type', 'password', 'validate_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        user_account = User(
            username=self.validated_data['username'],
            name=self.validated_data['name'],
            email=self.validated_data['email'],
            type=self.validated_data['type'],
        )
        password = self.validated_data['password']
        validate_password = self.validated_data['validate_password']

        if password != validate_password:
            raise serializers.ValidationError({'password': 'Passwords do not match, please try again.'})
        user_account.set_password(password)
        user_account.save()
        return user_account


class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItems
        fields = ('vendor', 'price', 'itemName', 'hidden')

    def save(self):
        menu_item = MenuItems(
            vendor=self.validated_data['vendor'],
            price=self.validated_data['price'],
            itemName=self.validated_data['itemName']
        )
        menu_item.save()
        return menu_item


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('item', 'qty', 'customer', 'orderPlaced', 'orderTime', 'status')


class MessUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessUser
        fields = ('breakfast_coupons', 'lunch_coupons', 'snacks_coupons', 'dinner_coupons')


class MessAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessAttendance
        fields = ('meal', 'date', 'attending', 'editable')


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('meal', 'date', 'feedback')


class FeedbackStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ('meal', 'date', 'feedback', 'status')


class DateDefaultMessMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultMessMenu
        fields = ('meal', 'item')


class DateMessMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessMenu
        fields = ('meal', 'items')


class DefaultMessMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = DefaultMessMenu
        fields = ('day', 'meal', 'items')


class AppFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppFeedback
        fields = ('feedback', )
