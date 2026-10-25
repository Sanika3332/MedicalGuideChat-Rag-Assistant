from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ConversationListCreateView,
    MessageListCreateView,
    RegisterView,
)

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("conversations/", ConversationListCreateView.as_view(), name="conversations"),
    path(
        "conversations/<int:conversation_id>/messages/",
        MessageListCreateView.as_view(),
        name="messages",
    ),
]