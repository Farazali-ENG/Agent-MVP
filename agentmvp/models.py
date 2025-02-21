from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from typing import Dict, List, Any



# Model for Customer Creation Manager (User)
class CustomerManager(BaseUserManager):
    def create_customer(self, email, password, role="user", **extra_fields):
        if not email or not password:
            raise ValueError("The Email and Password fields must be set")
        email = self.normalize_email(email)
        customer = self.model(email=email, role=role, **extra_fields)
        customer.set_password(password)

        extra_fields['is_staff'] = False
        extra_fields['is_superuser'] = False

        customer.save(using=self._db)
        
        return customer
    

    def create_superuser(self, email, password, role="admin", **extra_fields):
        if not email or not password:
            raise ValueError("The Email and Password fields must be set")
        email = self.normalize_email(email)
        customer = self.model(email=email, role=role, **extra_fields)
        customer.set_password(password)

        customer.is_staff = True
        customer.is_superuser = True

        customer.save(using=self._db)
        
        return customer


# Model for Customer (User)
class Customer(AbstractBaseUser):
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('customer', 'customer'),
    ]

    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, blank=False)
    password = models.CharField(max_length=255, blank=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_staff = models.BooleanField(default=False)  # Add the is_staff field
    is_superuser = models.BooleanField(default=False)  # Add the is_superuser field (if you want superuser functionality)

    objects = CustomerManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return (f"Name: {self.first_name} {self.last_name}")
    
    # Ensure that the user can access the admin panel if they are staff or a superuser
    def has_module_perms(self, app_label):
        # Superusers and staff should have access to all modules
        return self.is_superuser or self.is_staff

    # Check if the user has the permission to perform an action
    def has_perm(self, perm, obj=None):
        # Superusers have all permissions
        return self.is_superuser
    

class AgentUIConfig(models.Model):
    THEME_CHOICES = [
        ('light', 'light'),
        ('dark', 'dark'),
    ]

    primary_color = models.CharField(max_length=7, help_text="Hexadecimal color code for primary color", default="#000000")
    theme = models.CharField(max_length=5, choices=THEME_CHOICES, default='light')
    logo = models.FileField(upload_to='logos/', null=True, blank=True)
    greeting_message = models.CharField(max_length=255, default="Hi! How may I help you today?")
    auto_popup = models.BooleanField(default=False)


class Agent(models.Model):

    DATA_SCRAP_INTERVAL_CHOICES = [
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='customer')
    name = models.CharField(max_length=255)
    website_url = models.URLField(max_length=500)
    data_scrap_interval = models.CharField(
        max_length=10,
        choices=DATA_SCRAP_INTERVAL_CHOICES,
        default='weekly'
    )
    agent_information = models.TextField(blank=True, null=True)
    agent_prompt = models.TextField(blank=True, null=True)
    agent_temperature = models.FloatField(
        help_text="Enter a value between 0 and 1",
        default=1.0
    )
    
    agent_ui_config = models.ForeignKey(AgentUIConfig, on_delete=models.PROTECT, related_name='agent_ui_config', blank=True, null=True)


    def __str__(self):
        return self.name


class AgentDocument(models.Model):
    agent = models.ForeignKey(Agent, related_name='agent_docs', on_delete=models.CASCADE)
    document = models.FileField(upload_to='agent_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document {self.document.name} for {self.agent.name}"
    

class Visitor(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="Visitors_agent")
    uuid = models.UUIDField(blank=False)
    public_ip = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visitor on agent: {self.agent.name}, UUID: {self.uuid}"


class Chat(models.Model):
    ROLE_CHOICES = [
        ('visitor', 'visitor'),
        ('agent', 'agent')
    ]

    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='chats')
    chat_content = models.TextField(max_length=500)  # Limit content to 500 characters
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)  # Track the time chat was created
    updated_at = models.DateTimeField(auto_now=True)  # Track last update time

    def __str__(self):
        return f"Visitor ID: {self.visitor.id}, Role: {self.role}, Content: {self.chat_content}"


class Product(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100.0)
        ],
        help_text="Enter a value between 0 and 100",
        default=0,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.agent.name}"


class ResearchReport(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="research_reports")
    research_data = models.JSONField()  # Stores the complete research results
    website_summary = models.TextField()
    sales_strategy = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Research Report for {self.agent.name} - {self.created_at}"


class VisitorConversationState(models.Model):
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='conversation_states')
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name='visitor_states')
    current_phase = models.CharField(max_length=50, default='initial_greetings')
    conversation_history = models.JSONField(default=list)
    context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('visitor', 'agent')

    def append_to_history(self, role: str, content: str, phase: str = None):
        """Add a new message to conversation history with state information"""
        entry = {
            "role": role,
            "content": content,
            "phase": phase,
            "timestamp": datetime.now().isoformat()
        }
        
        history = self.conversation_history
        history.append(entry)
        self.conversation_history = history
        self.save()

    def update_context(self, key: str, value: Any):
        """Update context with new information"""
        context = self.context
        context[key] = value
        self.context = context
        self.save()

    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]

    def __str__(self):
        return f"Conversation State for Visitor {self.visitor.id} with Agent {self.agent.name}"

