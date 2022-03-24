from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import MoneyEntry, User, Category
from rest_framework.response import Response
from rest_framework import status

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'budget', 'email')

class UpdateUserSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data._mutable = True
        errors = {}
        checks = ['name', 'email']

        if data['password'] != '':
            data['password'] = make_password(data['password'])

        for check in checks:
            if check not in data or not data[check]:
                errors[check] = [f'{check} is required.']
        
        if bool(errors):
            raise serializers.ValidationError(errors)

        return data
    
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password')

class UserUpdateBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'budget')

    def validate(self, data):
        if 'budget' not in data or not data['budget']:
            raise serializers.ValidationError({ 'budget': ['budget is required.'] })

        return data

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'password', 'budget')

    def create(self, validated_data):
        if User.objects.filter(email = validated_data['email']).exists():
            raise serializers.ValidationError({ 'email': ['Email is already taken.'] })

        validated_data['password'] = make_password(validated_data['password'])

        return super().create(validated_data)
        
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'id', 'name', 'budget')

    def create(self, validated_data):
        user = User.objects.filter(email = validated_data['email'])
        

        if len(user) > 0 and check_password(validated_data['password'], user[0].password):
            return user[0]

        raise serializers.ValidationError({ 'error': ['Email or password is incorrect'] })

class MoneyEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyEntry
        fields = ('__all__')

    def validate(self, data):
        errors = {}
        checks = ['name', 'category', 'amount', 'date']

        for check in checks:
            if check not in data or not data[check]:
                errors[check] = [f'{check} is required.']
        
        if bool(errors):
            raise serializers.ValidationError(errors)

        return data

class ListMoneyEntrySerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = MoneyEntry
        fields = ('__all__')
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('__all__')

    def validate(self, data):
        if 'name' not in data:
            raise serializers.ValidationError({
                'name': ['name is required']
            })
        
        return data
