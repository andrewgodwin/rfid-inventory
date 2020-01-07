import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..models import Template


class ListTemplates(LoginRequiredMixin, ListView):
    queryset = Template.objects.all
    template_name = "checklist_templates/list.html"
    context_object_name = "templates"
    extra_context = {"section": "checklist_templates"}


class ViewTemplate(LoginRequiredMixin, DetailView):
    model = Template
    template_name = "checklist_templates/view.html"
    extra_context = {"section": "checklist_templates"}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["items_json"] = json.dumps(self.object.items_json())
        return context

    def post(self, request, *args, **kwargs):
        """
        Called to save the data
        """
        obj = self.get_object()
        data = json.loads(request.body)
        obj.save_items_json(data["items"])
        return JsonResponse({"items": obj.items_json()})


class EditTemplate(LoginRequiredMixin, UpdateView):
    model = Template
    fields = ["name"]
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "checklist_templates", "noun": "checklist template"}


class CreateTemplate(LoginRequiredMixin, CreateView):
    model = Template
    fields = ["name"]
    template_name = "generic/create.html"
    extra_context = {"section": "checklist_templates", "noun": "checklist template"}


class DeleteTemplate(LoginRequiredMixin, DeleteView):
    model = Template
    context_object_name = "obj"
    extra_context = {"section": "checklist_templates", "noun": "checklist template"}
    success_url = Template.urls.list
    template_name = "generic/delete.html"
