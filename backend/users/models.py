from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE = (
        (USER, 'Пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    )
    role = models.CharField(
        choices=ROLE,
        max_length=10,
        verbose_name='Роль пользователя',
        default=USER
    )
    username = models.CharField('username', max_length=150, unique=True)
    email = models.EmailField('e-mail', max_length=254, unique=True)
    first_name = models.TextField('first_name', max_length=150)
    last_name = models.TextField('last_name', max_length=150)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == self.ROLE

    def __str__(self):
        return self.username
