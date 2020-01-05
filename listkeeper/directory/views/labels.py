from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..models import Label


def index(request):
    return redirect(Label.urls.base)


class ListLabels(LoginRequiredMixin, ListView):
    queryset = Label.objects.order_by("name")
    template_name = "labels/list.html"
    context_object_name = "labels"
    extra_context = {"section": "labels"}


class EditLabel(LoginRequiredMixin, UpdateView):
    model = Label
    fields = ["name"]
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "labels", "noun": "label"}


class CreateLabel(LoginRequiredMixin, CreateView):
    model = Label
    fields = ["name"]
    template_name = "generic/create.html"
    extra_context = {"section": "labels", "noun": "label"}


class DeleteLabel(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "generic/delete.html"
    success_url = "/labels/"
    context_object_name = "obj"
    extra_context = {"section": "labels", "noun": "label"}
