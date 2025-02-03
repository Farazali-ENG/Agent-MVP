from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Agent, AgentUIConfig, Visitor, Chat, AgentDocument, Product
from .serializers import CustomerSerializer, AgentSerializer, AgentUIConfigSerializer, VisitorSerializer, ChatSerializer, ProductSerializer, AgentDocumentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .generate_agent_response import generate_response
from .scrap_products import product_scrapper, process_scraped_data
from .utils import generate_uuid_from_ip
import os
import json
from rest_framework_simplejwt.tokens import RefreshToken

from dotenv import load_dotenv

load_dotenv()


def check_authorized_access(current_user):
    
    if hasattr(current_user, 'role') and current_user.role == 'admin':
        return True
    
    return False

def check_current_user_access(current_user, customer_data_to_update):

    if current_user == customer_data_to_update:
        return True
    
    return False


class CustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None):

        if customer_id:
            
            try:
                customer = Customer.objects.get(id=customer_id)

                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)

                serializer = CustomerSerializer(customer)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching customer"}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method not allowed for customer role."}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                customers = Customer.objects.all()
                serializer = CustomerSerializer(customers, many=True)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching customers"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request):
        
        auth_access = check_authorized_access(request.user)
        if not auth_access:
            return Response({"message": "Method not allowed for customer role."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            # Save the new customer object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, customer_id):

        try:

            customer = Customer.objects.get(id=customer_id)

            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)

            
            serializer = CustomerSerializer(customer, data=request.data)
            if serializer.is_valid():
                # Save the new customer object
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)

    
    def delete(self, request, customer_id):

        try:
            customer = Customer.objects.get(id=customer_id)

            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Delete the customer instance
            customer.delete()
            return Response({"detail": "Customer deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Customer.DoesNotExist:
            return Response({"detail": "Customer not found."}, status=status.HTTP_404_NOT_FOUND)


    def patch(self, request, customer_id):
        try:
            customer = Customer.objects.get(id=customer_id)
            
            # Check authorization
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Partial update using existing CustomerSerializer
            serializer = CustomerSerializer(
                customer,
                data=request.data,
                partial=True  # This allows partial updates
            )
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(
                {"message": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Customer.DoesNotExist:
            return Response(
                {"message": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None, agent_id=None):
        
        if agent_id:
            
            try:
                agent = Agent.objects.get(id=agent_id, customer_id=customer_id)

                # Authenticate API
                customer = Customer.objects.get(id=customer_id)
                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
                
                serializer = AgentSerializer(agent)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching agent"}, status=status.HTTP_404_NOT_FOUND)
        
        if not agent_id and customer_id:
            
            try:
                agent = Agent.objects.filter(customer_id=customer_id)

                # Authenticate API
                customer = Customer.objects.get(id=customer_id)
                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
                
                serializer = AgentSerializer(agent, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching agents for customer."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            
            # Authenticate API
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method not allowed for customer role."}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                agents = Agent.objects.all()
                serializer = AgentSerializer(agents, many=True)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching agents"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request, customer_id=None):
        
        # Authenticate API
        auth_access = check_authorized_access(request.user)
        if not auth_access:
            return Response({"message": "Method not allowed for customer role."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()  # Ensure we can modify the data dictionary
        data['customer'] = customer_id  # Add customer to the data
        serializer = AgentSerializer(data=data)
        if serializer.is_valid():
            # Save the new agent object
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def patch(self, request, customer_id=None, agent_id=None):

        try:

            # Authenticate API
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method only allowed for admin."}, status=status.HTTP_401_UNAUTHORIZED)
            
            agent = Agent.objects.get(id=agent_id)
            serializer = AgentSerializer(instance=agent, data=request.data, partial=True)
            if serializer.is_valid():
                # Save the new agent object
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)
        
    
    def delete(self, request, customer_id=None, agent_id=None):

        try:
            
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method only allowed for admin."}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Delete the agent instance
            agent = Agent.objects.get(id=agent_id)
            agent.delete()
            return Response({"detail": "Agent deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        
        except Agent.DoesNotExist:
            return Response({"detail": "Agent not found."}, status=status.HTTP_404_NOT_FOUND)
        

class AgentUIConfigView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None, agent_id=None):
        
        if agent_id:
            
            try:

                # Authenticate API
                customer = Customer.objects.get(id=customer_id)
                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
                
                agent = Agent.objects.get(id=agent_id, customer_id=customer_id)
                agent_ui_config = agent.agent_ui_config
                serializer = AgentUIConfigSerializer(agent_ui_config)

                return Response(serializer.data, status=status.HTTP_200_OK)

            except:
                return Response({"error": "Error in fetching agent ui config."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            
            # Authenticate API
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method not allowed for customer role."}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                agent_ui_config = AgentUIConfig.objects.all()
                serializer = AgentUIConfigSerializer(agent_ui_config, many=True)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching agent ui configs."}, status=status.HTTP_404_NOT_FOUND)


    def patch(self, request, customer_id=None, agent_id=None):

        try:

            # Authenticate API
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response({"message": "Method only allowed for admin."}, status=status.HTTP_401_UNAUTHORIZED)
            
            agent = Agent.objects.get(id=agent_id, customer_id=customer_id)
            agent_ui_config = agent.agent_ui_config
            serializer = AgentUIConfigSerializer(instance=agent_ui_config, data=request.data, partial=True)
            if serializer.is_valid():
                # Save the new agent object
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Agent.DoesNotExist:
            return Response({"detail": "Agent UI Config not found."}, status=status.HTTP_404_NOT_FOUND)
        

# Contains authenticated views only for admin or current user
class VisitorView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None, agent_id=None, visitor_id=None):
        
        if visitor_id:
            
            try:
                visitor = Visitor.objects.get(id=visitor_id)
                serializer = VisitorSerializer(visitor)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching visitor."}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            
            # Authenticate API
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
                
            try:
                visitors = Visitor.objects.filter(agent=agent_id)
                serializer = VisitorSerializer(visitors, many=True)
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching visitors."}, status=status.HTTP_404_NOT_FOUND)


# Contains unauth views for Chatbot Message Processing
class UnauthVisitorView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, agent_id=None):
        try:
            public_ip = request.data.get('public_ip')
            if not public_ip:
                return Response(
                    {"message": "Public IP is required in request"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            uuid = generate_uuid_from_ip(public_ip)
            visitor = Visitor.objects.filter(uuid=uuid, agent_id=agent_id).first()
            
            if not visitor:
                return Response(
                    {"message": "No visitor found with this IP"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = VisitorSerializer(visitor)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, agent_id=None):
        try:
            public_ip = request.data.get('public_ip')
            if not public_ip:
                return Response(
                    {"message": "Public IP is required in request"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = {
                'agent': agent_id,
                'public_ip': public_ip
            }

            serializer = VisitorSerializer(data=data)
            if serializer.is_valid():
                visitor = serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Authenticated view to get visitor chats
class ChatView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None, agent_id=None, visitor_id=None):

        if visitor_id:

            try:

                # Authenticate API
                customer = Customer.objects.get(id=customer_id)
                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response({"message": "Method only allowed for admin and current user."}, status=status.HTTP_401_UNAUTHORIZED)
                
                chat = Chat.objects.filter(visitor_id=visitor_id).order_by('created_at')
                serializer = ChatSerializer(chat, many=True)

                return Response(serializer.data, status=status.HTTP_200_OK)
            
            except:
                return Response({"error": "Error in fetching chats for visitor."}, status=status.HTTP_404_NOT_FOUND)
            
        else:
            return Response({"error": "Invalid request."}, status=status.HTTP_404_NOT_FOUND)


# Unauthenticated chat view for Chatbot Message Processing
class UnauthChatView(APIView):

    permission_classes = [AllowAny]

    def post(self, request, agent_id, visitor_id):
        try:
            # Get the visitor
            visitor = Visitor.objects.get(id=visitor_id)
            
            # Get the agent and its related information
            agent = Agent.objects.get(id=agent_id)
            
            # Get agent documents
            agent_docs = AgentDocument.objects.filter(agent=agent)
            
            # Prepare business information JSON
            business_info = {
                "business_info": {
                    "name": agent.name,
                    "details": agent.agent_information
                }
            }
            
            # Prepare sales/technical information from documents
            # In a real implementation, you'd process the documents' content
            business_docs = {
                "documents": [doc.document.url for doc in agent_docs]
            }
            
            # Prepare agent configuration
            agent_config = {
                "system_prompt": agent.agent_prompt,
                "temperature": agent.agent_temperature
            }

            # Get products for the agent
            products = Product.objects.filter(agent_id=agent_id)
            product_serializer = ProductSerializer(products, many=True)
            product_data = product_serializer.data
            
            # Get user message from request
            user_message = request.data.get('message')
            if not user_message:
                return Response(
                    {"error": "Message is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate response using the imported function
            response = generate_response(
                business_info,
                agent_config,
                product_data,
                user_message
            )
            
            # Save the chat messages
            # Save visitor's message
            Chat.objects.create(
                visitor=visitor,
                chat_content=user_message,
                role='visitor'
            )
            
            # Save agent's response
            Chat.objects.create(
                visitor=visitor,
                chat_content=response,
                role='agent'
            )
            
            return Response({
                "response": response
            }, status=status.HTTP_200_OK)
            
        except Visitor.DoesNotExist:
            return Response(
                {"error": "Visitor not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Agent.DoesNotExist:
            return Response(
                {"error": "Agent not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Authenticated view to process preview chat
class ProcessPreviewChat(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, agent_id):
        try:
            # Check if user is admin
            auth_access = check_authorized_access(request.user)
            if not auth_access:
                return Response(
                    {"message": "Method only allowed for admin."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get the agent and its related information
            agent = Agent.objects.get(id=agent_id)
            
            # Get agent documents
            agent_docs = AgentDocument.objects.filter(agent=agent)
            
            # Prepare business information JSON
            business_info = {
                "business_info": {
                    "name": agent.name,
                    "details": agent.agent_information
                }
            }
            
            # Prepare sales/technical information from documents
            business_docs = {
                "documents": [doc.document.url for doc in agent_docs]
            }
            
            # Prepare agent configuration
            agent_config = {
                "system_prompt": agent.agent_prompt,
                "temperature": agent.agent_temperature
            }
            
            # Get products for the agent
            products = Product.objects.filter(agent_id=agent_id)
            product_serializer = ProductSerializer(products, many=True)
            product_data = product_serializer.data
            
            # Get user message from request
            user_message = request.data.get('message')
            if not user_message:
                return Response(
                    {"error": "Message is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate response using the imported function
            response = generate_response(
                business_info,
                agent_config,
                product_data,
                user_message
            )
            
            return Response({
                "response": response
            }, status=status.HTTP_200_OK)
            
        except Agent.DoesNotExist:
            return Response(
                {"error": "Agent not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# View to get and create products
class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id=None, agent_id=None, product_id=None):
        try:
            # Check authorization
            if customer_id:
                customer = Customer.objects.get(id=customer_id)
                auth_access = check_authorized_access(request.user)
                self_access = check_current_user_access(request.user, customer)
                if not auth_access and not self_access:
                    return Response(
                        {"message": "Method only allowed for admin and current user."}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )

            # Get single product
            if product_id:
                product = Product.objects.get(id=product_id, agent_id=agent_id)
                serializer = ProductSerializer(product)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Get all products for an agent
            elif agent_id:
                products = Product.objects.filter(agent_id=agent_id)
                serializer = ProductSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            # Get all products (admin only)
            else:
                if not check_authorized_access(request.user):
                    return Response(
                        {"message": "Method only allowed for admin."}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                products = Product.objects.all()
                serializer = ProductSerializer(products, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, customer_id=None, agent_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            data = request.data.copy()
            data['agent'] = agent_id
            
            serializer = ProductSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, customer_id=None, agent_id=None, product_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            product = Product.objects.get(id=product_id, agent_id=agent_id)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, customer_id=None, agent_id=None, product_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            product = Product.objects.get(id=product_id, agent_id=agent_id)
            product.delete()
            return Response(
                {"detail": "Product deleted successfully."}, 
                status=status.HTTP_204_NO_CONTENT
            )

        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# View to scrape products from website
class ScrapeProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, customer_id=None, agent_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get agent and website URL
            agent = Agent.objects.get(id=agent_id)
            website_url = agent.website_url

            # Scrape products
            try:
                scraped_data = product_scrapper(
                    api_key=os.getenv("OPENAI_API_KEY"),
                    source_links=[website_url]
                )
                products_data = json.loads(scraped_data)
                
                # Process the scraped data
                processed_products = process_scraped_data(products_data)
                
                # Create products from processed data
                created_products = []
                for product in processed_products:
                    product_data = {
                        'agent': agent_id,
                        'name': product['name'],
                        'price': product['price'],
                        'discount_percentage': product['discount_percentage'] or 0
                    }
                    
                    serializer = ProductSerializer(data=product_data)
                    if serializer.is_valid():
                        serializer.save()
                        created_products.append(serializer.data)
                
                if not created_products:
                    return Response(
                        {"error": "No valid products found in scraped data"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                return Response(
                    {
                        "message": f"Successfully scraped and created {len(created_products)} products",
                        "products": created_products
                    }, 
                    status=status.HTTP_201_CREATED
                )
                
            except Exception as e:
                return Response(
                    {"error": f"Error scraping products: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Customer.DoesNotExist:
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Agent.DoesNotExist:
            return Response(
                {"error": "Agent not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Logout View
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Successfully logged out"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class GetUserIdView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Get the user from the request (automatically handled by IsAuthenticated)
            user = request.user
            
            # Use CustomerSerializer to get all fields except password
            serializer = CustomerSerializer(user)
            
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentDocumentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, customer_id=None, agent_id=None, document_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            if document_id:
                # Get specific document
                document = AgentDocument.objects.get(id=document_id, agent_id=agent_id)
                serializer = AgentDocumentSerializer(document)
            else:
                # Get all documents for agent
                documents = AgentDocument.objects.filter(agent_id=agent_id)
                serializer = AgentDocumentSerializer(documents, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (Customer.DoesNotExist, Agent.DoesNotExist, AgentDocument.DoesNotExist):
            return Response(
                {"message": "Requested resource not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, customer_id=None, agent_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Verify agent exists
            agent = Agent.objects.get(id=agent_id)
            
            # Add agent_id to the request data
            data = request.data.copy()
            data['agent'] = agent_id
            
            serializer = AgentDocumentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {"message": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        except (Customer.DoesNotExist, Agent.DoesNotExist):
            return Response(
                {"message": "Customer or Agent not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, customer_id=None, agent_id=None, document_id=None):
        try:
            # Check authorization
            customer = Customer.objects.get(id=customer_id)
            auth_access = check_authorized_access(request.user)
            self_access = check_current_user_access(request.user, customer)
            if not auth_access and not self_access:
                return Response(
                    {"message": "Method only allowed for admin and current user."}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            document = AgentDocument.objects.get(id=document_id, agent_id=agent_id)
            document.delete()
            return Response(
                {"message": "Document deleted successfully"}, 
                status=status.HTTP_204_NO_CONTENT
            )

        except (Customer.DoesNotExist, Agent.DoesNotExist, AgentDocument.DoesNotExist):
            return Response(
                {"message": "Requested resource not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UnauthAgentUIConfigView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, agent_id=None):
        try:
            # Get the agent's UI config
            agent = Agent.objects.get(id=agent_id)
            agent_ui_config = agent.agent_ui_config
            
            if not agent_ui_config:
                return Response(
                    {"message": "No UI config found for this agent"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = AgentUIConfigSerializer(agent_ui_config)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Agent.DoesNotExist:
            return Response(
                {"message": "Agent not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"message": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



