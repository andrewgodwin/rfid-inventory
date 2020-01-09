import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)

from devices.models import Device
from ..forms import RunForm, SetupScanForm
from ..models import Run


class ListRuns(LoginRequiredMixin, ListView):
    queryset = Run.objects.select_related("template")
    template_name = "checklist_runs/list.html"
    context_object_name = "runs"
    extra_context = {"section": "checklist_runs"}


class ViewRun(LoginRequiredMixin, DetailView):
    json = False
    model = Run
    template_name = "checklist_runs/view.html"
    extra_context = {"section": "checklist_runs"}

    def get(self, *args, **kwargs):
        if self.json:
            obj = self.get_object()
            return JsonResponse({"items": obj.items_json()})
        else:
            return super().get(*args, **kwargs)

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
        return JsonResponse({"ok": True})


class ViewRunAPI(LoginRequiredMixin, DetailView):
    """
    Returns current Run status as JSON
    """

    model = Run
    template_name = "checklist_runs/view.html"
    extra_context = {"section": "checklist_runs"}

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


class EditRun(LoginRequiredMixin, UpdateView):
    model = Run
    form_class = RunForm
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "checklist_runs", "noun": "checklist run"}


class CreateRun(LoginRequiredMixin, CreateView):
    model = Run
    form_class = RunForm
    template_name = "generic/create.html"
    extra_context = {"section": "checklist_runs", "noun": "checklist run", "next": True}

    def get_success_url(self):
        return self.object.urls.post_create


class PostCreateRun(LoginRequiredMixin, UpdateView):
    model = Run
    form_class = RunForm
    template_name = "generic/create.html"
    context_object_name = "obj"
    extra_context = {"section": "checklist_runs", "noun": "checklist run"}


class DeleteRun(LoginRequiredMixin, DeleteView):
    model = Run
    context_object_name = "obj"
    extra_context = {"section": "checklist_runs", "noun": "checklist run"}
    success_url = Run.urls.list
    template_name = "generic/delete.html"


class SetupScan(LoginRequiredMixin, FormView):
    """
    Wizard to assign a location to a device, this run, and to turn the device to
    associate mode.
    """
    form_class = SetupScanForm
    template_name = "checklist_runs/setup_scan.html"
    extra_context = {"section": "checklist_runs"}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["run"] = Run.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        run = Run.objects.get(pk=self.kwargs['pk'])
        device = form.cleaned_data["device"]
        location = form.cleaned_data["location"]
        # Assign the location to us
        run.locations.add(location)
        # Find all devices with that location currently and turn off association
        Device.objects.filter(location=location).update(mode="passive")
        # Assign it to the device and put it into association mode
        device.location = location
        device.mode = "assigning"
        device.save()
        return redirect(run.urls.view)


class StopScan(LoginRequiredMixin, View):
    """
    Removes location assignment from the run and disables
    assignment mode on devices.
    """

    def get(self, *args, **kwargs):
        # Get run
        run = Run.objects.get(pk=self.kwargs['pk'])
        # Go through all devices with our locations and turn off association
        Device.objects.filter(location__in=run.locations.all()).update(mode="passive")
        # Remove all locations
        run.locations.clear()
        return redirect(run.urls.view)
