from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rag.generator import LLMError
from rag.service import answer_question

from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    RegisterSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MessageListCreateView(generics.GenericAPIView):
    serializer_class = MessageSerializer

    def get_conversation(self):
        return get_object_or_404(
            Conversation,
            pk=self.kwargs["conversation_id"],
            user=self.request.user,
        )

    def get(self, request, conversation_id):
        conversation = self.get_conversation()
        serializer = self.get_serializer(conversation.messages.all(), many=True)
        return Response(serializer.data)

    def post(self, request, conversation_id):
        conversation = self.get_conversation()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.save(
            conversation=conversation, role=Message.Role.USER
        )

        try:
            answer, sources = answer_question(user_message.content)
        except LLMError:
            return Response(
                {"detail": "The answer service is unavailable right now. Please try again."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        assistant_message = Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=answer,
            sources=sources,
        )
        return Response(
            {
                "user_message": MessageSerializer(user_message).data,
                "assistant_message": MessageSerializer(assistant_message).data,
            },
            status=status.HTTP_201_CREATED,
        )