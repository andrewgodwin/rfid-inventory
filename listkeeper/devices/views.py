from bs4 import BeautifulSoup

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
    patch_ids = ["device-last-seen", "recent-reads"]

    def get(self, request, *args, **kwargs):
        # Don't handle non-patch requests
        template_response = super().get(request, *args, **kwargs)
        if not request.GET.get("patch", None):
            return template_response
        # OK, they want a patch, so render the template and extract the right pieces
        template_response.render()
        soup = BeautifulSoup(template_response.content, "html.parser")
        json_response = {}
        for id in self.patch_ids:
            json_response[id] = " ".join(soup.find(id=id).decode_contents().split())
        return JsonResponse(json_response)


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
