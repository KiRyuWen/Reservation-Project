from django.contrib import admin
from loginapp.models import customer
from loginapp.models import Room
from loginapp.models import Book

#from .models import *

# Register your models here.


class customerAdmin(admin.ModelAdmin):
    list_display = ('cName', 'cEmail')


class roomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'rName')


admin.site.register(customer, customerAdmin)
admin.site.register(Room, roomAdmin)
admin.site.register(Book)
