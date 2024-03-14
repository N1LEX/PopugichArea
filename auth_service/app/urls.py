from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from app.views import TokenCreateView, SigninView, AuthenticateAppView, UserCreateView

urlpatterns = [
    path('signup/', UserCreateView.as_view()),
    path('authenticate/', AuthenticateAppView.as_view()),
    path('signin/', SigninView.as_view(), name="signin"),
    path('token/create/', TokenCreateView.as_view(), name="create-token"),
    path('token/refresh/', TokenRefreshView.as_view(), name="refresh-token"),
    path('token/verify/', TokenVerifyView.as_view(), name="verify-token"),
]
