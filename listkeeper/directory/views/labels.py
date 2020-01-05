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
    template_name = "labels/edit.html"
    extra_context = {"section": "labels"}


class CreateLabel(LoginRequiredMixin, CreateView):
    model = Label
    fields = ["name"]
    template_name = "labels/create.html"
    extra_context = {"section": "labels"}


class DeleteLabel(LoginRequiredMixin, DeleteView):
    model = Label
    template_name = "labels/delete.html"
    extra_context = {"section": "labels"}
    success_url = "/labels/"
