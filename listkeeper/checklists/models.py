import urlman

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.functional import cached_property


class Template(models.Model):
    """
    A main checklist. Instances of this get checked off.
    """

    name = models.CharField(max_length=255, unique=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        list = "/checklists/templates/"
        view = "{list}{self.id}/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.urls.view

    def sync_items(self):
        """
        Runs sync_items on all Runs underneath this template
        """
        for run in self.runs.all():
            run.sync_items()

    @cached_property
    def conditions(self):
        """
        Returns a list of conditions that this checklist needs to be run
        """
        return sorted(set(x.strip() for x in self.items.values_list("condition", flat=True) if x.strip()))

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
        # Finally, re-sync items to runs
        self.sync_items()


class TemplateItem(models.Model):
    """
    A tickable-off item on a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE, related_name="items")

    order = models.IntegerField(default=0)
    heading = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    condition = models.CharField(max_length=255, blank=True)
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
            "condition": self.condition,
            "labels": self.labels,
            "quantity": self.quantity,
        }

    def from_json(self, data):
        self.name = data["name"]
        self.heading = data.get("heading", False)
        self.description = data.get("description", "")
        self.condition = data.get("condition", "")
        self.labels = data.get("labels", "")
        self.quantity = data.get("quantity", 1)


class Run(models.Model):
    """
    A usage/instance of a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE, related_name="runs")
    name = models.CharField(max_length=255, unique=True)

    conditions = JSONField(blank=True, null=True)  # List of conditions that are true

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class urls(urlman.Urls):
        list = "/checklists/runs/"
        view = "{list}{self.id}/"
        post_create = "{view}post-create/"
        edit = "{view}edit/"
        delete = "{view}delete/"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return self.urls.view

    def save(self):
        super().save()
        self.sync_items()

    def sync_items(self):
        """
        Synchronises the RunItems so they match the template.
        """
        # Get two lists of the IDs each side has, filtered according to the conditions
        template_item_ids = set()
        for template_item in self.template.items.all():
            if (not template_item.condition) or (template_item.condition in (self.conditions or [])):
                template_item_ids.add(template_item.id)
        run_item_ids = set(self.run_items.values_list("template_item_id", flat=True))
        # Delete IDs we have but they don't
        self.run_items.filter(template_item_id__in=run_item_ids.difference(template_item_ids)).delete()
        # And make items for IDs they have and we don't
        for template_item_id in template_item_ids.difference(run_item_ids):
            self.run_items.create(template_item_id=template_item_id)

    def items_json(self):
        """
        Returns our items in a standard JSON format the frontend understands
        """
        return [item.to_json() for item in self.run_items.select_related("template_item").order_by("template_item__order")]

    def save_items_json(self, json_items):
        """
        Given data in the JSON format, saves our items as it.
        """
        seen_ids = set()
        for json_item in json_items:
            # Find item by ID
            try:
                run_item = self.run_items.get(id=json_item["id"])
            except RunItem.DoesNotExist:
                continue
            # Set the state
            checked = json_item.get("checked", False)
            skipped = json_item.get("skipped", False)
            if run_item.checked != checked or run_item.skipped != skipped:
                run_item.checked = checked
                run_item.skipped = skipped
                run_item.save()


class RunItem(models.Model):
    """
    A tickable-off item on a checklist, with option item associations
    """

    run = models.ForeignKey("checklists.Run", on_delete=models.CASCADE, related_name="run_items")
    template_item = models.ForeignKey("checklists.TemplateItem", on_delete=models.CASCADE, related_name="run_items")

    checked = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    items = models.ManyToManyField("directory.Item")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ("run", "template_item"),
        ]

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.template_item.name,
            "heading": self.template_item.heading,
            "description": self.template_item.description,
            "labels": self.template_item.labels,
            "quantity": self.template_item.quantity,
            "checked": self.checked,
            "skipped": self.skipped,
        }
