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
    queryset = Item.objects.select_related("location").prefetch_related("labels", "images").order_by("name")
    template_name = "items/list.html"
    context_object_name = "items"
    extra_context = {"section": "items"}


class ViewItem(LoginRequiredMixin, DetailView):
    model = Item
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
