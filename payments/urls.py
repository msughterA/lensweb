from django.urls import path
from . import  views


urlpatterns = [
   path('card',views.CardSubscriptionView.as_view(),name='card'),
   path('pin',views.PinSubscriptionView.as_view(),name='pin')
]