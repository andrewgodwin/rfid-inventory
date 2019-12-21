"""listkeeper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin, auth
from django.urls import path

from directory.views import items, labels, locations
from devices import api, views as devices

urlpatterns = [
    path("", items.index),
    # Auth
    path("auth/login/", auth.views.LoginView.as_view(template_name="login.html")),
    path("auth/logout/", auth.views.LogoutView.as_view()),
    # Items
    path("items/", items.ListItems.as_view()),
    path("items/create/", items.CreateItem.as_view()),
    path("items/<int:pk>/", items.ViewItem.as_view()),
    path("items/<int:pk>/edit/", items.EditItem.as_view()),
    path("items/<int:pk>/delete/", items.DeleteItem.as_view()),
    # Devices
    path("devices/", devices.ListDevices.as_view()),
    path("devices/create/", devices.CreateDevice.as_view()),
    path("devices/<int:pk>/", devices.ViewDevice.as_view()),
    path("devices/<int:pk>/edit/", devices.EditDevice.as_view()),
    path("devices/<int:pk>/delete/", devices.DeleteDevice.as_view()),
    path("devices/<int:pk>/set-mode/<str:mode>/", devices.SetDeviceMode.as_view()),
    # Locations
    path("locations/", locations.ListLocations.as_view()),
    path("locations/create/", locations.CreateLocation.as_view()),
    path("locations/reparent/", locations.ReparentLocation.as_view()),
    path("locations/<int:pk>/", locations.ViewLocation.as_view()),
    path("locations/<int:pk>/edit/", locations.EditLocation.as_view()),
    path("locations/<int:pk>/delete/", locations.DeleteLocation.as_view()),
    # Labels
    path("labels/", labels.ListLabels.as_view()),
    path("labels/create/", labels.CreateLabel.as_view()),
    path("labels/<int:pk>/", labels.ViewLabel.as_view()),
    path("labels/<int:pk>/edit/", labels.EditLabel.as_view()),
    path("labels/<int:pk>/delete/", labels.DeleteLabel.as_view()),
    # API URLs
    path("api/device/sync/", api.sync),
    # Admin delegation
    path("admin/", admin.site.urls),
]
