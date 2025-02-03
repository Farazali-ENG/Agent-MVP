from django.contrib import admin
from .models import Customer, Agent, AgentDocument, AgentUIConfig, Visitor, Chat, Product
# Register your models here.


admin.site.register(Customer)
admin.site.register(Agent)
admin.site.register(AgentDocument)
admin.site.register(AgentUIConfig)
admin.site.register(Visitor)
admin.site.register(Chat)
admin.site.register(Product)