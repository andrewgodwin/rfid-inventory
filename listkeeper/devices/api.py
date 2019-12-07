import json
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Device, DeviceRead


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
    update_reads(device, data.get("tags", []))
    # Send back a mode
    return JsonResponse({"mode": "passive"})


def update_reads(device, tags):
    """
    Updates the device's DeviceRead objects with the new tags seen.
    """
    seen_time = timezone.now()
    tags = set(tags)
    # For each tag, update its record
    for tag in tags:
        try:
            read = DeviceRead.objects.get(device=device, tag=tag)
        except DeviceRead.DoesNotExist:
            read = DeviceRead(device=device, tag=tag)
        read.last_seen = seen_time
        read.present = True
        read.save()
    # Set tags that are no longer visible to not present
    DeviceRead.objects.filter(last_seen__lt=seen_time, present=True).update(
        present=False
    )
