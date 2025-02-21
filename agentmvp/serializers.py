from rest_framework import serializers
from .models import Customer, Agent, AgentDocument, AgentUIConfig, Visitor, Chat, Product, ResearchReport, VisitorConversationState
from .utils import generate_uuid_from_ip
from .run_research import run_research
import asyncio
from .retrieval_agent.chromadb_agent import chunk_and_store, initialize_client
from .retrieval_agent.web_scraper import get_content
import chromadb


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
    research_report = serializers.SerializerMethodField()
    agent_ui_config = AgentUIConfigSerializer(required=False)
    agent_docs = serializers.ListField(child=serializers.FileField(), required=False, write_only=True)
    agent_temperature = serializers.FloatField(
        help_text="Enter a value between 0 and 1",
        default=1.0
    )
    data_scrap_interval = serializers.ChoiceField(choices=Agent.DATA_SCRAP_INTERVAL_CHOICES, default='weekly')

    class Meta:
        model = Agent
        fields = ["id", "customer", "name", "website_url", "data_scrap_interval", "agent_information",
                   "agent_docs", "agent_ui_config", "agent_temperature", "agent_prompt", "research_report"]

    def get_research_report(self, obj):
        report = ResearchReport.objects.filter(agent=obj).order_by('-created_at').first()
        if report:
            return {
                'id': report.id,
                'research_data': report.research_data,
                'website_summary': report.website_summary,
                'sales_strategy': report.sales_strategy,
                'created_at': report.created_at
            }
        return None

    def create(self, validated_data):
        agent_ui_config = validated_data.pop('agent_ui_config', None)
        agent_docs = validated_data.pop('agent_docs', [])
        
        # Create agent
        agent = Agent.objects.create(**validated_data)
        
        # Create UI config if provided
        if agent_ui_config:
            ui_config = AgentUIConfig.objects.create(**agent_ui_config)
            agent.agent_ui_config = ui_config
            agent.save()
        else:
            # Create default UI config and associate with agent
            ui_config = AgentUIConfig.objects.create()
            agent.agent_ui_config = ui_config
            agent.save()
        
        # Create documents if provided
        for doc in agent_docs:
            AgentDocument.objects.create(agent=agent, document=doc)
        
        # Run research if website_url is provided
        if agent.website_url:
            try:
                research_results = asyncio.run(self._generate_research_report(agent))
                if research_results:
                    ResearchReport.objects.create(
                        agent=agent,
                        research_data=research_results.get('research', {}),
                        website_summary=research_results.get('website_summary', ''),
                        sales_strategy=research_results.get('strategy', '')
                    )
            except Exception as e:
                print(f"Error generating research report: {str(e)}")
        
        # Create vector store for agent
        if agent.website_url:
            try:
                collection, text_splitter = initialize_client(agent.name.replace(" ", ""))
                content = get_content(agent.website_url)
                chunk_and_store(collection, text_splitter, content)
                print(f"Vector store created for agent {agent.id}")
            except Exception as e:
                print(f"Error creating vector store: {str(e)}")
        
        return agent

    async def _generate_research_report(self, agent):
        """Generate research report using WebResearchManager"""
        from .run_research import async_run_research
        
        try:
            research_results = await async_run_research(agent.name, agent.website_url)
            return research_results
        except Exception as e:
            print(f"Error in research generation: {str(e)}")
            return None
    
    def update(self, instance, validated_data):
        agent_ui_config = validated_data.pop('agent_ui_config', None)
        agent_docs = validated_data.pop('agent_docs', [])

        # Update agent UI config if provided
        if agent_ui_config:
            AgentUIConfig.objects.update_or_create(
                agent=instance,
                defaults=agent_ui_config
            )

        # Add new documents if provided
        for doc in agent_docs:
            AgentDocument.objects.create(agent=instance, document=doc)

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
    
    def delete(self, instance):
        try:
            # Initialize ChromaDB client
            client = chromadb.PersistentClient(path="./chroma_db")
            
            # Delete the collection if it exists
            collection_name = instance.name.replace(" ", "")
            try:
                client.delete_collection(name=collection_name)
                print(f"Deleted ChromaDB collection for agent {instance.id}")
            except Exception as e:
                print(f"Error deleting ChromaDB collection: {str(e)}")
                
        except Exception as e:
            print(f"Error connecting to ChromaDB: {str(e)}")
            
        # Call the parent's delete method
        return super().delete(instance)


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
    

class ResearchReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchReport
        fields = ['id', 'agent', 'research_data', 'sales_strategy', 'website_summary', 'created_at', 'updated_at']


class ConversationHistoryEntrySerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()
    phase = serializers.CharField()
    timestamp = serializers.DateTimeField()

class VisitorConversationStateSerializer(serializers.ModelSerializer):
    conversation_history = ConversationHistoryEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = VisitorConversationState
        fields = [
            'id',
            'visitor',
            'agent',
            'current_phase',
            'conversation_history',
            'context',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_current_phase(self, value):
        valid_phases = [
            "initial_greetings",
            "ask_name",
            "ask_clarification_questions",
            "offer_solution",
            "ask_biggest_concerns",
            "ask_what_prevents_from_making_decision",
            "lead_closing",
            "end_phase",
            "intermediate_phase"
        ]
        if value not in valid_phases:
            raise serializers.ValidationError(f"Invalid phase. Must be one of: {', '.join(valid_phases)}")
        return value

    def validate_context(self, value):
        if 'last_analysis' in value:
            required_fields = [
                'key_concerns_or_interests',
                'trust_signals',
                'recommended_product_or_service_to_sell',
                'customer_confidence_in_the_product_or_service'
            ]
            for field in required_fields:
                if field not in value['last_analysis']:
                    raise serializers.ValidationError(f"Psychological analysis missing required field: {field}")
        return value