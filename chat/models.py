from django.db import models
from django.conf import settings

# Create your models here.
class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
           on_delete = models.CASCADE,
           related_name = "conversations",
           )
    title = models.CharField(max_length=200,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ["created_at"]

def __str__(self):
    return f"{self.title or 'Untitled'} ({self.user})"


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user","User"
        ASSISTANT = "assistant","Assistant"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name = "messages",
    )
    role = models.CharField(max_length=10,choices=Role.choices)
    content = models.TextField()
    sources = models.JSONField(default=list,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Meta:
    ordering = ["created_at"]

def __str__(self):
    return f"{self.role}: {self.content[:40]}"
    

