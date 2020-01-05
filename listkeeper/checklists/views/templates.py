from django.contrib.auth.mixins import LoginRequiredMixin
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
    queryset = Template.objects
    template_name = "checklist_templates/list.html"
    context_object_name = "templates"
    extra_context = {"section": "checklist_templates"}


class ViewTemplate(LoginRequiredMixin, DetailView):
    model = Template
    template_name = "checklist_templates/view.html"
    extra_context = {"section": "checklist_templates"}


class EditTemplate(LoginRequiredMixin, UpdateView):
    model = Template
    fields = ["name"]
    template_name = "checklist_templates/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "checklist_templates"}


class CreateTemplate(LoginRequiredMixin, CreateView):
    model = Template
    fields = ["name"]
    template_name = "generic/create.html"
    extra_context = {"section": "checklist_templates", "noun": "checklist template"}


class DeleteTemplate(LoginRequiredMixin, DeleteView):
    model = Template
    context_object_name = "obj"
    extra_context = {"section": "labels", "noun": "label"}
    success_url = Template.urls.list
    template_name = "generic/delete.html"
