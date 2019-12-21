import uuid

import urlman

from django.db import models
from django.utils import functional, timezone


class Tag(models.Model):
    """
    A reference to a single physical tag.

    We allow for multiple tags per physical item.
    """

    id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Type prefix, colon, hex value of tag (e.g. epc:f376ce13434a2b)",
    )
    item = models.ForeignKey(
        "directory.Item",
        blank=True,
        null=True,
        related_name="tags",
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class Item(models.Model):
    """
    A physical item, with zero or more tags on it.
    """

    name = models.CharField(max_length=255, help_text="Unique-ish name of the item")
    description = models.TextField(blank=True, help_text="General item description")
    serial = models.TextField(
        blank=True, help_text="Item serial number/other unique ID"
    )
    notes = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(blank=True, null=True)
    deleted = models.DateTimeField(blank=True, null=True)

    location = models.ForeignKey(
        "directory.Location",
        related_name="items",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    labels = models.ManyToManyField("directory.Label", related_name="items", blank=True)

    def __str__(self):
        return "%s: %s" % (self.id, self.name)

    def get_absolute_url(self):
        return self.urls.view

    class urls(urlman.Urls):
        base = "/items/"
        view = "{base}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def recent_reads(self):
        """
        Returns a curated list of sightings
        """
        return self.device_reads.order_by("-last_seen")[:5]

    def recent_locations(self):
        """
        A short location history
        """
        return self.location_histories.order_by("-timestamp")[:5]

    def set_location(self, location):
        """
        Adds an appearance in a location, if it wasn't already there.
        """
        if self.location != location:
            self.location_histories.create(location=location, timestamp=timezone.now())
            self.location = location
            self.save(update_fields=["location"])

    @functional.cached_property
    def image(self):
        """
        Returns an image if there is one
        """
        if self.images.exists():
            return self.images.all()[0].image
        return None


class ItemImage(models.Model):
    """
    Images of an item. They have an order; the first one is considered primary.
    """

    item = models.ForeignKey(
        "directory.Item", related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="items/images/%Y%m/")
    order = models.IntegerField(default=0)


class Label(models.Model):
    """
    An arbitary categorisation of Items, many allowed. Anywhere else, would be
    called "tag", but that's not a great word to re-use here.
    """

    name = models.CharField(max_length=100, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        base = "/labels/"
        view = "{base}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.urls.view


class Location(models.Model):
    """
    A location that objects can be in.

    Locations may be nested inside other locations.
    """

    name = models.CharField(
        max_length=255,
        help_text="Name of location (use / for hierarchies)",
        unique=True,
    )

    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    class urls(urlman.Urls):
        list = "/locations/"
        create = "{list}create/"
        view = "{list}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"
        items = "/items/?location={self.name}"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.urls.view


class LocationHistory(models.Model):
    """
    A log of when an item moved locations.
    """

    item = models.ForeignKey(
        "directory.Item", related_name="location_histories", on_delete=models.PROTECT
    )
    location = models.ForeignKey(
        "directory.Location",
        related_name="location_histories",
        on_delete=models.PROTECT,
    )
    timestamp = models.DateTimeField()

    class Meta:
        verbose_name_plural = "location histories"

    def __str__(self):
        return "%s: %s in %s at %s" % (
            self.id,
            self.item,
            self.location,
            self.timestamp,
        )
