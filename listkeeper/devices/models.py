import datetime
import random
import urlman

from django.db import models
from django.utils import functional, timezone

from directory.models import Tag


class Device(models.Model):
    """
    A (handheld or fixed) RFID reading/writing device.
    """

    MODE_CHOICES = [
        ("passive", "Passive tracking"),
        ("assigning", "Assigning locations"),
    ]

    name = models.CharField(max_length=200, help_text="Unique-ish device name")
    type = models.CharField(max_length=200, blank=True, help_text="Device type")
    notes = models.TextField(blank=True)
    token = models.TextField(blank=True, help_text="Device API token")

    mode = models.CharField(
        max_length=32,
        choices=MODE_CHOICES,
        default=MODE_CHOICES[0][0],
        help_text="Current device mode",
    )
    location = models.ForeignKey(
        "directory.Location", blank=True, null=True, on_delete=models.SET_NULL
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    last_seen = models.DateTimeField(blank=True, null=True)

    class urls(urlman.Urls):
        list = "/devices/"
        view = "{list}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"
        set_assigning = "{view}set-mode/assigning/"
        set_passive = "{view}set-mode/passive/"

    def __str__(self):
        return "#%s: %s" % (self.id, self.name)

    def get_absolute_url(self):
        return self.urls.view

    def save(self):
        if not self.token:
            self.token = "".join(
                random.choice("23456789abcdefghkmnpqrstuvwxyz") for _ in range(32)
            )
        super().save()

    def recent_reads(self):
        """
        Returns a QuerySet of "recent" device reads to show in the UI
        """
        return self.reads.order_by("-last_seen")[:20]


class DeviceRead(models.Model):
    """
    Incoming reads of tags in the field of a device. Transient; deleted
    after a retention period. In some ways, a bad message queue.

    Devices will do some of their own buffering and de-duplication; we do not
    want to have the same tag in here once a second, though, even if they send it.
    """

    device = models.ForeignKey(
        "devices.Device", on_delete=models.CASCADE, related_name="reads"
    )
    tag = models.CharField(
        max_length=255,
        help_text="Type prefix, colon, hex value of tag (e.g. epc:f376ce13434a2b)",
    )
    item = models.ForeignKey(
        "directory.Item",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="device_reads",
    )

    created = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField()
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = [("device", "tag")]

    def __str__(self):
        return "%s seen by %s at %s" % (self.tag, self.device, self.last_seen)

    @functional.cached_property
    def directory_tag(self):
        """
        Gets the Directory Tag object that corresponds with this read, or None
        if there is not one.
        """
        try:
            return Tag.objects.select_related("item").get(id=self.tag)
        except Tag.DoesNotExist:
            return None
