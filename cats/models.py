from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models

CHOICES = (
    ('Gray', 'Серый'),
    ('Black', 'Чёрный'),
    ('White', 'Белый'),
    ('Ginger', 'Рыжий'),
    ('Mixed', 'Смешанный'),
)

ROLE_CHOICES = (
    ('owner', 'Владелец'),
    ('moderator', 'Модератор'),
    ('employee', 'Сотрудник'),
)

User = get_user_model()

phone_validator = RegexValidator(
    regex=r'^\+?\d{7,15}$',
    message='Номер телефона должен содержать от 7 до 15 цифр '
            'и может начинаться с «+».',
)


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16, choices=CHOICES)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', on_delete=models.CASCADE)
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')

    class Meta:
        constraints = [
         models.UniqueConstraint(
             fields=['name', 'owner'],
             name='unique_name_owner'
            )
        ]
    
    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Shelter(models.Model):
    name = models.CharField(max_length=128)
    address = models.CharField(max_length=256)
    phone = models.CharField(
        max_length=20, blank=True, validators=[phone_validator])
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User, related_name='owned_shelters', on_delete=models.CASCADE)
    cats = models.ManyToManyField(Cat, related_name='shelters', blank=True)
    capacity = models.PositiveIntegerField(
        default=50,
        help_text='Максимальное количество котов в приюте.')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShelterEmployee(models.Model):
    shelter = models.ForeignKey(
        Shelter, related_name='employees', on_delete=models.CASCADE)
    user = models.ForeignKey(
        User, related_name='shelter_jobs', on_delete=models.CASCADE)
    role = models.CharField(
        max_length=16, choices=ROLE_CHOICES, default='employee')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['shelter', 'user'],
                name='unique_shelter_employee',
            )
        ]

    def __str__(self):
        return f'{self.user} — {self.get_role_display()} @ {self.shelter}'
