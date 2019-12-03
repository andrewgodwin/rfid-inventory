from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404

from ..models import Item


def tag_get(request, tag_id):
    """
    Returns information about the tag.
    """
    try:
        tag = Tag.objects.select_related("item").get(id=tag_id)
    except Tag.DoesNotExist:
        pass
    return JsonResponse(
        {
            "id": tag.id,
            "item": {
                "id": tag.item.id,
                "name": tag.item.name,
                "serial": tag.item.serial,
            },
        }
    )


def tag_seen(request, tag_id, location_id):
    """
    Called when a tag is seen in the wild.
    """
    pass
