from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from loginapp.models import customer
from loginapp.models import Room
from loginapp.models import Book
from django import forms
#from .models import *

# Register your models here.


class customerAdminForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=customer.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=('session members'),
            is_stacked=False
        )
    )


class roomAdmin(admin.ModelAdmin):
    list_display = ('room_id', 'rName')


class customerAdmin(admin.ModelAdmin):
    list_display = ('cName', 'cEmail')
    form = customerAdminForm


class BookAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'date', 'time_id', 'meetingName')
    filter_horizontal = ('sessionMember',)


admin.site.register(customer, customerAdmin)
admin.site.register(Room, roomAdmin)
admin.site.register(Book, BookAdmin)
