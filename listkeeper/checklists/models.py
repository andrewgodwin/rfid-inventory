import urlman

from django.db import models


class Template(models.Model):
    """
    A main checklist. Instances of this get checked off.
    """

    name = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        list = "/checklists/templates/"
        view = "{list}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)

    def get_absolute_url(self):
        return self.urls.view

    def items_json(self):
        """
        Returns our items in a standard JSON format the frontend understands
        """
        return [item.to_json() for item in self.items.order_by("order")]

    def save_items_json(self, json_items):
        """
        Given data in the JSON format, saves our items as it.
        """
        seen_ids = set()
        for i, json_item in enumerate(json_items):
            # Find item by ID
            item = TemplateItem(template=self)
            if isinstance(json_item["id"], int):
                try:
                    item = self.items.get(id=json_item["id"])
                except TemplateItem.DoesNotExist:
                    pass
            # Update it
            item.order = i + 1
            item.from_json(json_item)
            item.save()
            seen_ids.add(item.id)
        # Now, remove any deleted items
        self.items.exclude(id__in=seen_ids).delete()


class TemplateItem(models.Model):
    """
    A tickable-off item on a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE, related_name="items")

    order = models.IntegerField(default=0)
    heading = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    question = models.CharField(max_length=255, blank=True)
    labels = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "heading": self.heading,
            "description": self.description,
            "question": self.question,
            "labels": self.labels,
            "quantity": self.quantity,
        }

    def from_json(self, data):
        self.name = data["name"]
        self.heading = data.get("heading", False)
        self.description = data.get("description", "")
        self.question = data.get("question", "")
        self.labels = data.get("labels", "")
        self.quantity = data.get("quantity", 1)


class Run(models.Model):
    """
    A usage/instance of a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE, related_name="runs")
    name = models.CharField(max_length=255)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        list = "/checklists/runs/"
        view = "{list}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)


class RunItem(models.Model):
    """
    A tickable-off item on a checklist, with option item associations
    """

    run = models.ForeignKey("checklists.Run", on_delete=models.CASCADE, related_name="run_items")
    item = models.ForeignKey("checklists.TemplateItem", on_delete=models.CASCADE, related_name="run_items")

    checked = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    items = models.ManyToManyField("directory.Item")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)
