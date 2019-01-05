from django.contrib import admin
from .models import Hobby, Message, PendingRequest, User

# Register your models here.

admin.site.register(Hobby)
admin.site.register(Message)
admin.site.register(PendingRequest)
admin.site.register(User)
