from django.contrib import admin

from .models import FoodgramUser, Subscription

admin.site.register(FoodgramUser)
admin.site.register(Subscription)