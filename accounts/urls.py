from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView
)

app_name = "accounts"
urlpatterns = [
    path("", views.signup, name="signup"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),

    path("<str:username>/", views.UserDetailAPIView.as_view(), name="profile"),
    path("<str:username>/my/", views.my, name="my"),
    path("<str:username>/like/", views.like, name="like"),
    
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
