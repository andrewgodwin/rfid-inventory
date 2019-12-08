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


class ListItems(ListView):
    queryset = Item.objects.select_related("location").order_by("name")
    template_name = "items/list.html"
    context_object_name = "items"
    extra_context = {"section": "items"}


class ViewItem(DetailView):
    model = Item
    template_name = "items/view.html"
    extra_context = {"section": "items"}


class EditItem(UpdateView):
    model = Item
    form_class = EditItemForm
    template_name = "items/edit.html"
    extra_context = {"section": "items"}


class CreateItem(CreateView):
    model = Item
    form_class = CreateItemForm
    template_name = "items/create.html"
    extra_context = {"section": "items"}

    def get_initial(self):
        if "tag" in self.request.GET:
            return {"tag": self.request.GET["tag"]}


class DeleteItem(DeleteView):
    model = Item
    template_name = "items/delete.html"
    success_url = "/items/"
