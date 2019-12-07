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
from django.contrib import admin
from django.urls import path

from directory.views import items
from devices import api, views as devices

urlpatterns = [
    path("", items.index),
    path("items/", items.ListItems.as_view()),
    path("items/create/", items.CreateItem.as_view()),
    path("items/<int:pk>/", items.ViewItem.as_view()),
    path("items/<int:pk>/edit/", items.EditItem.as_view()),
    path("items/<int:pk>/delete/", items.DeleteItem.as_view()),
    path("devices/", devices.ListDevices.as_view()),
    path("devices/create/", devices.CreateDevice.as_view()),
    path("devices/<int:pk>/", devices.ViewDevice.as_view()),
    path("devices/<int:pk>/edit/", devices.EditDevice.as_view()),
    path("devices/<int:pk>/delete/", devices.DeleteDevice.as_view()),
    path("api/device/sync/", api.sync),
    path("admin/", admin.site.urls),
]
