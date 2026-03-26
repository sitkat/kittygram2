from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

import datetime as dt

from .models import (
    CHOICES, ROLE_CHOICES, Achievement, AchievementCat,
    Cat, Shelter, ShelterEmployee, User,
)


class UserSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cats')
        ref_name = 'ReadOnlyUsers'


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(many=True, required=False)
    color = serializers.ChoiceField(choices=CHOICES)
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'achievements', 'owner',
                  'age')
        read_only_fields = ('owner',)
        validators = [
            UniqueTogetherValidator(
                queryset=Cat.objects.all(),
                fields=('name', 'owner')
                )
            ]

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement)
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
            return cat
        
    def validate(self, data):
        if data['color'] == data['name']:
            raise serializers.ValidationError('Имя не может совпадать с цветом!')
        return data
        
    def validate_birth_year(self, value):
        year = dt.date.today().year
        if not (year - 40 < value <= year):
            raise serializers.ValidationError('Проверьте год рождения!')
        return value


class ShelterEmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ShelterEmployee
        fields = ('id', 'shelter', 'user', 'username', 'role', 'joined_at')
        read_only_fields = ('shelter', 'joined_at')

    def validate_role(self, value):
        if value == 'owner':
            raise serializers.ValidationError(
                'Роль «владелец» назначается автоматически.')
        return value

    def validate(self, data):
        shelter = self.context.get('shelter')
        user = data.get('user')
        if shelter and user:
            if ShelterEmployee.objects.filter(
                    shelter=shelter, user=user).exists():
                raise serializers.ValidationError(
                    'Этот пользователь уже является сотрудником приюта.')
        return data


class ShelterSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault())
    cats = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Cat.objects.all(), required=False)
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Shelter
        fields = (
            'id', 'name', 'address', 'phone', 'description',
            'owner', 'cats', 'capacity', 'employee_count', 'created_at')
        read_only_fields = ('owner', 'created_at')

    def get_employee_count(self, obj):
        return obj.employees.count()

    def validate_cats(self, value):
        shelter = self.instance
        capacity = (
            self.initial_data.get('capacity')
            or (shelter.capacity if shelter else 50)
        )
        if len(value) > int(capacity):
            raise serializers.ValidationError(
                f'Количество котов ({len(value)}) превышает '
                f'вместимость приюта ({capacity}).')
        return value

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Вместимость приюта должна быть минимум 1.')
        if value > 1000:
            raise serializers.ValidationError(
                'Вместимость приюта не может превышать 1000.')
        return value
