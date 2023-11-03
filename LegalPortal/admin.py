from django.contrib import admin
from .models import Client,Lawyer,Transactions

# 
admin.site.register(Transactions)
admin.site.register(Client)
admin.site.register(Lawyer)

# Register your models here.
