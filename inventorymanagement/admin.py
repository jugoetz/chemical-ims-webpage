from django.contrib import admin
from .models import Bottle, ChangeListEntry

# Register your models here.


class BottleAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['id']}),
        ('Bottle information', {'fields': ['description', 'supplier', 'price', 'quantity']}),
        ('Location information', {'fields': ['owner', 'code', 'location']}),
        ('Status information', {'fields': ['status', 'borrowed_two_weeks']}),
        ('Last borrower information', {'fields': ['borrower_full_name', 'borrower_group', 'borrower_email']}),
    ]
    list_display = ('id', 'code', 'location', 'status', 'checkout_date', 'borrowed_two_weeks')
    list_filter = ['status', 'borrower_group', 'owner_group']
    search_fields = ['id']
    actions = ['mark_checked_out', 'mark_checked_in']

    def mark_checked_out(self, request, queryset):
        queryset.update(status='out')
    mark_checked_out.short_description = "Mark selected bottles as checked out"

    def mark_checked_in(self, request, queryset):
        queryset.update(status='in')
    mark_checked_in.short_description = "Mark selected bottles as checked in"


class ChangeListEntryAdmin(admin.ModelAdmin):
    fields = ['date', 'description']
    list_display = ['entry_id', 'date', 'description']


admin.site.register(Bottle, BottleAdmin)
admin.site.register(ChangeListEntry, ChangeListEntryAdmin)
