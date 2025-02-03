from rest_framework import serializers
from .models import Customer, Agent, AgentDocument, AgentUIConfig, Visitor, Chat, Product
from .utils import generate_uuid_from_ip


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.CharField(required=True)
    role = serializers.ChoiceField(choices=Customer.ROLE_CHOICES, default='customer')

    class Meta:
        model = Customer
        fields = ['id', 'email', 'password', 'role', 'first_name', 'last_name', 'phone_number']
        extra_kwargs = {
            'role': {'default': 'User'},  # Default role for new users
        }

    def create(self, validated_data):
        
        # Create the customer using the manager's method
        customer = Customer.objects.create_customer(**validated_data)

        return customer

    def validate(self, data):
        user_id = self.instance.id if self.instance else None  # Get current user's ID for update checks

        if data.get("email"):
            # Check if the email is already used by another customer
            if Customer.objects.filter(email=data.get("email")).exclude(id=user_id).exists():
                raise serializers.ValidationError("A user with this email already exists.")

        return data
    

class AgentDocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgentDocument
        fields = ["id", "agent", "document", "uploaded_at"]


class AgentUIConfigSerializer(serializers.ModelSerializer):

    theme = serializers.ChoiceField(choices=AgentUIConfig.THEME_CHOICES, default="light")

    class Meta:
        model = AgentUIConfig
        fields = ["id", "primary_color", "theme", "logo", "greeting_message", "auto_popup"]


class AgentSerializer(serializers.ModelSerializer):

    data_scrap_interval = serializers.ChoiceField(choices=Agent.DATA_SCRAP_INTERVAL_CHOICES, default='weekly')
    agent_ui_config = AgentUIConfigSerializer(required=False)
    agent_docs = serializers.ListField(child=serializers.FileField(), required=False, write_only=True)
    agent_temperature = serializers.FloatField(
        help_text="Enter a value between 0 and 1",
        default=1.0
    )

    class Meta:
        model = Agent
        fields = ["id", "customer", "name", "website_url", "data_scrap_interval", "agent_information",
                   "agent_docs", "agent_ui_config", "agent_temperature", "agent_prompt"]
    
    def create(self, validated_data):

        # Separating the data for connected models
        agent_docs_data = validated_data.pop('agent_docs', [])
        agent_ui_config_data = validated_data.pop('agent_ui_config', None)

        # Create the agent
        agent = Agent.objects.create(**validated_data)

        if agent_ui_config_data:
            ui_config = AgentUIConfig.objects.create(**agent_ui_config_data)
        else:
            ui_config = AgentUIConfig.objects.create()
        agent.agent_ui_config = ui_config

        for file in agent_docs_data:
            AgentDocument.objects.create(agent=agent, document=file)

        agent.save()
        return agent
    
    def update(self, instance, validated_data):

        # Update fields of the Agent instance
        instance.name = validated_data.get('name', instance.name)
        instance.website_url = validated_data.get('website_url', instance.website_url)
        instance.data_scrap_interval = validated_data.get('data_scrap_interval', instance.data_scrap_interval)
        instance.agent_information = validated_data.get('agent_information', instance.agent_information)
        instance.agent_prompt = validated_data.get('agent_prompt', instance.agent_prompt)
        instance.agent_temperature = validated_data.get('agent_temperature', instance.agent_temperature)

        instance.save()
        return instance
    
    def validate_agent_temperature(self, value):
        if not 0.0 <= value <= 1.0:
            raise serializers.ValidationError("The agent temperature must be between 0 and 1.")
        return value

    def to_representation(self, instance):

        """Customize the serialized output to include business_docs."""
        representation = super().to_representation(instance)
        representation['agent_docs'] = AgentDocumentSerializer(instance.agent_docs.all(), many=True).data
        
        return representation
    

class VisitorSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(required=False)
    public_ip = serializers.CharField(required=True)
    
    class Meta:
        model = Visitor
        fields = ["id", "agent", "uuid", "created_at", "updated_at", "public_ip"]

    def create(self, validated_data):
        public_ip = validated_data.get("public_ip", "")

        if not public_ip:
            raise serializers.ValidationError("Public IP required to create visitor.")

        uuid = generate_uuid_from_ip(public_ip)
        existing_visitors = Visitor.objects.filter(uuid=uuid, agent=validated_data["agent"])
        if existing_visitors:
            raise serializers.ValidationError("Visitor already exists.")

        validated_data["uuid"] = uuid
        visitor = Visitor.objects.create(**validated_data)
        visitor.save()

        return visitor


class ChatSerializer(serializers.ModelSerializer):
    
    visitor = VisitorSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    discount_percentage = serializers.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Enter a value between 0 and 100"
    )

    class Meta:
        model = Product
        fields = ["id", "agent", "name", "price", "discount_percentage"]
    
    def validate_discount_percentage(self, value):
        if not 0.0 <= value <= 100.0:
            raise serializers.ValidationError("The discount percentage must be between 0 and 100.")
        return value