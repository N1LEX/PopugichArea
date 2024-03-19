from django.urls import path, include

urlpatterns = [
    path('', include('accounting.urls')),
]
