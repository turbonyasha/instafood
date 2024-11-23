from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class FoodgramUser(AbstractUser):
    """Модель пользователя с дополнительным
    полем аватарки и ролями."""

    ROLES = [
        ('user', 'Пользователь'),
        ('admin', 'Администратор')
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default='user',
        verbose_name='Роль'
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Аватар',
        default='media/'
    )
    is_subscribed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return settings.MEDIA_URL + 'avatars/default-avatar.png'


class Subscription(models.Model):
    """Модель для подписок пользователя."""
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers',
        null=True,
        verbose_name='Автор рецептов'
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
