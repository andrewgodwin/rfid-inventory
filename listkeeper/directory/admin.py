from django.contrib import admin

from .models import Tag, Item, Label, Location, LocationHistory

admin.site.register(Tag)
admin.site.register(Label)
admin.site.register(Location)
admin.site.register(LocationHistory)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["name", "serial", "notes", "location", "labels"]}),
        ("Timestamps", {"fields": ["created", "updated", "deleted"]}),
    ]
    list_display = ["id", "name", "serial", "location", "created", "updated"]
    list_display_links = ["id", "name"]
    readonly_fields = ["created", "updated"]
