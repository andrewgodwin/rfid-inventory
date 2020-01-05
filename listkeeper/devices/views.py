import random
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
    View,
)

from .models import Device, DeviceWrite


class ListDevices(LoginRequiredMixin, ListView):
    queryset = Device.objects.select_related("location").order_by("name")
    template_name = "devices/list.html"
    context_object_name = "devices"
    extra_context = {"section": "devices"}


class ViewDevice(LoginRequiredMixin, DetailView):
    queryset = Device.objects.prefetch_related("reads", "writes").select_related("location")
    template_name = "devices/view.html"
    extra_context = {"section": "devices"}
    patch_ids = ["device-last-seen", "recent-reads", "writes"]

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
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "devices", "noun": "device"}


class CreateDevice(LoginRequiredMixin, CreateView):
    model = Device
    fields = ["name", "type", "location", "notes"]
    template_name = "generic/create.html"
    extra_context = {"section": "devices", "noun": "device"}


class DeleteDevice(LoginRequiredMixin, DeleteView):
    model = Device
    template_name = "generic/delete.html"
    success_url = "/devices/"
    context_object_name = "obj"
    extra_context = {"section": "devices", "noun": "device"}


class SetDeviceMode(LoginRequiredMixin, DetailView):
    model = Device

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mode = kwargs["mode"]
        self.object.save()
        return redirect(self.object.urls.view)


class AddWrite(LoginRequiredMixin, CreateView):
    model = DeviceWrite
    fields = ["device", "tag"]
    template_name = "devices/add-write.html"
    extra_context = {"section": "devices"}

    def get_initial(self):
        return {"device": self.kwargs["pk"]}

    def get_success_url(self):
        return self.object.device.urls.view


class AddRandomWrite(LoginRequiredMixin, View):
    """
    Creates a random tag to write to the device
    """

    def get(self, request, pk):
        tag_suffix = "".join(random.choice("abcdef1234567890") for i in range(22))
        self.object = DeviceWrite.objects.create(device_id=pk, tag="epc:e2%s" % tag_suffix)
        return redirect(self.object.device.urls.view)
