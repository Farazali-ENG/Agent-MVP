# urls.py

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomerView, AgentView, AgentUIConfigView, VisitorView, UnauthCreateVisitorView, UnauthGetVisitorView, ChatView, UnauthChatView, ProcessPreviewChat, ProductView, ScrapeProductsView, LogoutView, GetUserIdView, AgentDocumentView, UnauthAgentUIConfigView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [

    # Customer APIs
    path('customer/all/', CustomerView.as_view(), name="get_customer"),
    path('customer/get/<int:customer_id>/', CustomerView.as_view(), name="get_all_customer"),
    path('customer/update/<int:customer_id>/', CustomerView.as_view(), name="update_customer"),
    path('customer/create/', CustomerView.as_view(), name="register_user"),
    path('customer/delete/<int:customer_id>/', CustomerView.as_view(), name="delete_user"),
    path('customer/get-id/', GetUserIdView.as_view(), name="get_user_id"),

    # Login APIs
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Agent URLs
    path('customer/<int:customer_id>/agent/create/', AgentView.as_view(), name="create_agent"),
    path('agent/all/', AgentView.as_view(), name="get_all_agents"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/', AgentView.as_view(), name="get_update_or_delete_agent"),
    path('customer/<int:customer_id>/agent/all/', AgentView.as_view(), name="get_all_agents_for_customer"),

    # Agent UI Config URLs
    path('agentuiconfig/all/', AgentUIConfigView.as_view(), name="get_all_ui_configs"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/agentuiconfig/', AgentUIConfigView.as_view(), name="get_or_update_ui_config"),
    # Unauth Agent UI Config URL
    path('agent/<int:agent_id>/uiconfig/', UnauthAgentUIConfigView.as_view(), name="get_unauth_ui_config"),

    # Unauth Visitor URLs
    path('agent/<int:agent_id>/visitor/create/', UnauthCreateVisitorView.as_view(), name="create_visitor"),
    path('agent/<int:agent_id>/visitor/get-by-ip/', UnauthGetVisitorView.as_view(), name="get_visitor_by_ip"),
    # Visitor URLs
    path('customer/<int:customer_id>/agent/<int:agent_id>/visitor/all/', VisitorView.as_view(), name="get_all_visitors_for_agent"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/visitor/<int:visitor_id>/', VisitorView.as_view(), name="get_visitor_by_id"),

    # Chat URLs
    path('customer/<int:customer_id>/agent/<int:agent_id>/visitor/<int:visitor_id>/chat/all/', ChatView.as_view(), name="get_all_chats_for_visitor"),
    path('agent/<int:agent_id>/visitor/<int:visitor_id>/chat/create/', UnauthChatView.as_view(), name="create_chat_for_visitor"),
    # Preview Chat URL
    path('customer/<int:customer_id>/agent/<int:agent_id>/preview-chat/', ProcessPreviewChat.as_view(), name="preview_chat"),

    # Product URLs
    path('products/all/', ProductView.as_view(), name="get_all_products"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/products/', ProductView.as_view(), name="get_create_products"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/products/<int:product_id>/', ProductView.as_view(), name="get_update_delete_product"),

    # Scrape Products URL
    path('customer/<int:customer_id>/agent/<int:agent_id>/products/scrape/', ScrapeProductsView.as_view(), name="scrape_products"),

    # Agent Document URLs
    path('customer/<int:customer_id>/agent/<int:agent_id>/document/create/', AgentDocumentView.as_view(), name="create_agent_document"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/document/all/', AgentDocumentView.as_view(), name="get_all_agent_documents"),
    path('customer/<int:customer_id>/agent/<int:agent_id>/document/<int:document_id>/', AgentDocumentView.as_view(), name="get_or_delete_agent_document"),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)