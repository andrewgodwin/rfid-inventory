from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .models import Device


class ListDevices(LoginRequiredMixin, ListView):
    queryset = Device.objects.order_by("name")
    template_name = "devices/list.html"
    context_object_name = "devices"
    extra_context = {"section": "devices"}


class ViewDevice(LoginRequiredMixin, DetailView):
    model = Device
    template_name = "devices/view.html"
    extra_context = {"section": "devices"}


class EditDevice(LoginRequiredMixin, UpdateView):
    model = Device
    fields = ["name", "type", "location", "notes"]
    template_name = "devices/edit.html"
    extra_context = {"section": "devices"}


class CreateDevice(LoginRequiredMixin, CreateView):
    model = Device
    fields = ["name", "type", "location", "notes"]
    template_name = "devices/create.html"
    extra_context = {"section": "devices"}


class DeleteDevice(LoginRequiredMixin, DeleteView):
    model = Device
    template_name = "devices/delete.html"
    success_url = "/devices/"


class SetDeviceMode(LoginRequiredMixin, DetailView):
    model = Device

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mode = kwargs["mode"]
        self.object.save()
        return redirect(self.object.urls.view)
