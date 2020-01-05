from django.contrib import admin

from .models import Template, Run


admin.site.register(Template)
admin.site.register(Run)
