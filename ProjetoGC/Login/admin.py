from django.contrib import admin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ( 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
# Register your models here.
