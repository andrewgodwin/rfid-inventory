from django import forms

from .models import Item


class CreateItemForm(forms.ModelForm):

    tag = forms.CharField(
        required=False, help_text="Optional tag to immediately associate with"
    )

    class Meta:
        model = Item
        fields = ["name", "description", "serial", "notes"]
        widgets = {"description": forms.TextInput(), "serial": forms.TextInput()}

    def save(self, **kwargs):
        instance = super().save(**kwargs)
        # If we got a tag, add that too
        if self.cleaned_data["tag"]:
            instance.tags.create(id=self.cleaned_data["tag"])
        return instance
