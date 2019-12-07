from django.contrib import admin

from .models import Device, DeviceRead


admin.site.register(Device)


@admin.register(DeviceRead)
class DeviceReadAdmin(admin.ModelAdmin):
    list_display = ["id", "device", "tag", "last_seen", "present"]
