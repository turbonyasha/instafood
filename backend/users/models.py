from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    """Модель пользователя с дополнительным
    полем аватарки и подписки."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(
        verbose_name='Имя',
        blank=False,
        null=False,
        max_length=128
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        blank=False,
        null=False,
        max_length=128
    )
    avatar = models.ImageField(
        blank=True,
        null=True,
        verbose_name='Аватар',
        upload_to='avatar/image'
    )
    is_subscribed = models.BooleanField(
        default=False,
        verbose_name='В подписках',
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


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
        ordering = ('subscribed_at',)
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_author_in_subscriptions'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
