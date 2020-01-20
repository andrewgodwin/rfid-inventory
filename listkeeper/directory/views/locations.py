from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
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

from ..forms import LocationForm, ReparentForm
from ..models import Location


class ListLocations(LoginRequiredMixin, ListView):
    queryset = Location.objects.order_by("name").annotate(
        items_count=models.Count("items")
    )
    template_name = "locations/list.html"
    context_object_name = "locations"
    extra_context = {"section": "locations"}


class ViewLocation(LoginRequiredMixin, DetailView):
    model = Location
    template_name = "locations/view.html"
    extra_context = {"section": "locations"}


class EditLocation(LoginRequiredMixin, UpdateView):
    model = Location
    form_class = LocationForm
    template_name = "generic/edit.html"
    context_object_name = "obj"
    extra_context = {"section": "locations", "noun": "location"}


class CreateLocation(LoginRequiredMixin, CreateView):
    model = Location
    form_class = LocationForm
    template_name = "generic/create.html"
    extra_context = {"section": "locations", "noun": "location", "add_another": True}

    def get_success_url(self):
        if "add-another" in self.request.POST:
            messages.add_message(
                self.request,
                messages.INFO,
                "Created Location <a href='{}'>{}</a>".format(
                    self.object.urls.view, self.object.name
                ),
            )
            return "{}?created={}".format(Location.urls.create, self.object.id)
        return super().get_success_url()


class DeleteLocation(LoginRequiredMixin, DeleteView):
    model = Location
    template_name = "generic/delete.html"
    success_url = "/locations/"
    context_object_name = "obj"
    extra_context = {"section": "locations", "noun": "location"}


class ReparentLocation(LoginRequiredMixin, FormView):
    template_name = "locations/reparent.html"
    form_class = ReparentForm
    extra_context = {"section": "locations"}

    def form_valid(self, form):
        changes = self.calculate_changes(
            form.cleaned_data["name"], form.cleaned_data["new_name"]
        )
        # See if we're definitely reparenting yet, or if we should show a confirmation screen.
        if "confirmed" in self.request.POST:
            # Rename the locations
            for old, new in changes:
                location = Location.objects.get(name=old)
                location.name = new
                location.save()
            # Redirect
            return redirect(Location.urls.list)
        # Otherwise, show a confirmation screen
        else:
            context = self.get_context_data(form=form)
            context["renames"] = changes
            context["confirming"] = True
            return self.render_to_response(context)

    def calculate_changes(self, name, new_name):
        """
        Calculates a list of location names and what they become.
        """
        results = []
        for location in Location.objects.filter(name__startswith=name):
            results.append(
                (
                    location.name,
                    LocationForm.normalise_name(new_name + location.name[len(name) :]),
                )
            )
        results.sort()
        return results


class ClearLocation(LoginRequiredMixin, View):
    """
    Removes all items from this location.
    """

    def get(self, *args, **kwargs):
        # Get location
        location = Location.objects.get(pk=self.kwargs['pk'])
        # Go through all items in that location and remove them from it
        location.items.update(location=None)
        return redirect(location.urls.view)
