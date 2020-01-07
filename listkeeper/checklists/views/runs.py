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

from ..forms import RunForm
from ..models import Run


class ListRuns(LoginRequiredMixin, ListView):
    queryset = Run.objects.select_related("template")
    template_name = "checklist_runs/list.html"
    context_object_name = "runs"
    extra_context = {"section": "checklist_runs"}


class ViewRun(LoginRequiredMixin, DetailView):
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
