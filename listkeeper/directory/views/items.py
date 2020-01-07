from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from ..models import Item
from ..forms import CreateItemForm, EditItemForm


def index(request):
    return redirect(Item.urls.base)


class ListItems(LoginRequiredMixin, ListView):
    template_name = "items/list.html"
    context_object_name = "items"
    extra_context = {"section": "items"}

    def get_queryset(self, *args, **kwargs):
        qs = Item.objects.select_related("location").prefetch_related("labels", "images").order_by("name")
        if "search" in self.request.GET:
            qs = qs.filter(name__icontains=self.request.GET["search"])
        if "location" in self.request.GET:
            qs = qs.filter(location__name=self.request.GET["location"])
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["search"] = self.request.GET.get("search", "")
        context["location"] = self.request.GET.get("location", "")
        return context


class ViewItem(LoginRequiredMixin, DetailView):
    queryset = Item.objects.select_related("location").prefetch_related("labels", "images")
    template_name = "items/view.html"
    extra_context = {"section": "items"}


class EditItem(LoginRequiredMixin, UpdateView):
    model = Item
    form_class = EditItemForm
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "items", "noun": "item"}


class CreateItem(LoginRequiredMixin, CreateView):
    model = Item
    form_class = CreateItemForm
    template_name = "generic/create.html"
    extra_context = {"section": "items", "noun": "item"}

    def get_initial(self):
        if "tag" in self.request.GET:
            return {"tag": self.request.GET["tag"]}


class DeleteItem(LoginRequiredMixin, DeleteView):
    model = Item
    template_name = "generic/delete.html"
    success_url = "/items/"
    context_object_name = "obj"
    extra_context = {"section": "items", "noun": "item"}
