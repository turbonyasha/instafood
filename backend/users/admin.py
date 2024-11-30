from django.contrib import admin

from .models import FoodgramUser, Subscription


class FoodgramUserAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name', 'username', 'email')


admin.site.register(FoodgramUser)
admin.site.register(Subscription)
