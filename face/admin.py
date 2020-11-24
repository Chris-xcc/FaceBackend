from django.contrib import admin

# Register your models here.
from face.models import User, Sign

admin.site.register(User)
admin.site.register(Sign)
