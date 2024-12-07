from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from api.views import SubscriptionListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/users/subscriptions/',
        SubscriptionListView.as_view(),
        name='subscriptions-list'
    ),
    path(
        'api/users/<int:id>/subscribe/',
        SubscriptionListView.as_view(),
        name='user-subscribe'
    ),
    path('', include('api.urls', namespace='api')),
    path('', include('recipes.urls', namespace='recipes')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
