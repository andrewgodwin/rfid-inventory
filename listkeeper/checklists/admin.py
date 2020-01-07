from django.contrib import admin

from .models import Template, Run, TemplateItem, RunItem


admin.site.register(Template)
admin.site.register(TemplateItem)
admin.site.register(Run)
admin.site.register(RunItem)
