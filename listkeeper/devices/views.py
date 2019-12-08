from django.shortcuts import render
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Device


class ListDevices(ListView):
    queryset = Device.objects.order_by("name")
    template_name = "devices/list.html"
    context_object_name = "devices"
    extra_context = {"section": "devices"}


class ViewDevice(DetailView):
    model = Device
    template_name = "devices/view.html"
    extra_context = {"section": "devices"}


class EditDevice(UpdateView):
    model = Device
    fields = ["name", "type", "notes"]
    template_name = "devices/edit.html"
    extra_context = {"section": "devices"}


class CreateDevice(CreateView):
    model = Device
    fields = ["name", "type", "notes"]
    template_name = "devices/create.html"
    extra_context = {"section": "devices"}


class DeleteDevice(DeleteView):
    model = Device
    template_name = "devices/delete.html"
    success_url = "/devices/"
