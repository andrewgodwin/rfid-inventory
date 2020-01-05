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


class TemplateItem(models.Model):
    """
    A tickable-off item on a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE)

    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    heading = models.BooleanField(default=False)

    question = models.CharField(max_length=255, blank=True)
    labels = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)


class Run(models.Model):
    """
    A usage/instance of a checklist
    """

    template = models.ForeignKey("checklists.Template", on_delete=models.CASCADE)
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

    run = models.ForeignKey("checklists.Run", on_delete=models.CASCADE)
    item = models.ForeignKey("checklists.TemplateItem", on_delete=models.CASCADE)

    checked = models.BooleanField(default=False)
    skipped = models.BooleanField(default=False)
    items = models.ManyToManyField("directory.Item")

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%i)" % (self.name, self.id)
