from django.db import models


class ChatSession(models.Model):
    """Sesión de conversación por usuario y empresa"""
    session_id = models.CharField(max_length=100, unique=True)
    tenant_schema = models.CharField(max_length=100)  # schema del tenant activo
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'chatbot_session'

    def __str__(self):
        return f"Session {self.session_id} - {self.tenant_schema}"


class ChatMessage(models.Model):
    """Mensaje individual dentro de una sesión"""
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    intent = models.CharField(max_length=50, blank=True, null=True)  # intención detectada
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chatbot_message'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:50]}"
