from django.contrib import admin
from .models import gear_value

@admin.register(gear_value)
class  gear_valueAdmin(admin.ModelAdmin):
    list_display = ['date','time','value']