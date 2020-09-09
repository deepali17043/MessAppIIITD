from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from . models import User, MenuItems, Cart


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('username', 'name', 'email', 'userType')
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', ]
            )
        ]


class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItems
        fields = ('vendor', 'price', 'itemName', 'hidden')


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ('item', 'qty', 'customer', 'orderPlaced', 'orderTime', 'status')
