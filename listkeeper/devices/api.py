import json
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Device, DeviceRead, DeviceWrite


@csrf_exempt
def sync(request):
    """
    Called by a device to submit RFID tags it sees.

    The tags are sent as a JSON-encoded HTTP body.
    """
    # Load the body
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"error": "Invalid HTTP body"}, status=400)
    # Work out device via token
    try:
        device = Device.objects.get(token=data["token"])
    except Device.DoesNotExist:
        return JsonResponse({"error": "Invalid token"}, status=400)
    # Handle any RFID tags it's seen
    reads = update_reads(device, data.get("tags", []))
    # Handle any writes
    update_writes(device, data.get("written", []))
    # Ping that we saw it
    Device.objects.filter(id=device.id).update(last_seen=timezone.now())
    # Grab the next pending write
    write = None
    if device.writes.exists():
        write = device.writes.order_by("created")[0].tag
    # Send back a mode
    return JsonResponse({"mode": "passive", "write": write, "tag_names": reads})


def update_reads(device, tag_values):
    """
    Updates the device's DeviceRead objects with the new tags seen.
    """
    result = {}
    seen_time = timezone.now()
    tag_values = set(tag_values)
    # For each tag, update its record
    for tag_value in tag_values:
        # See if an RSSI is bundled in
        if "/" in tag_value:
            tag, rssi = tag_value.split("/", 1)
        else:
            tag, rssi = tag_value, None
        # Clean the tag value
        tag = tag.replace(" ", "").lower()
        # Fetch the database row
        try:
            read = DeviceRead.objects.get(device=device, tag=tag)
        except DeviceRead.DoesNotExist:
            read = DeviceRead(device=device, tag=tag)
        read.last_seen = seen_time
        read.present = True
        read.rssi = rssi
        # See if we can associate it with an item
        if read.directory_tag and read.directory_tag.item:
            read.item = read.directory_tag.item
            result[tag_value] = read.item.name
            # And see if we're in location-assigning mode!
            if device.mode == "assigning" and device.location:
                read.item.set_location(device.location)
        read.save()
    # Set tags that are no longer visible to not present
    DeviceRead.objects.filter(
        device=device, last_seen__lt=seen_time, present=True
    ).update(present=False)
    return result


def update_writes(device, tag_values):
    """
    Updates the device's DeviceWrite objects to remove any that were written
    """
    DeviceWrite.objects.filter(device=device, tag__in=tag_values).delete()
