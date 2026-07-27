from django import forms
from .models import Card


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ["front", "back", "category", "chapter", "topic", "trap", "is_active"]
        widgets = {
            "front": forms.TextInput(attrs={"class": "input"}),
            "back": forms.Textarea(attrs={"class": "input", "rows": 4}),
            "category": forms.Select(attrs={"class": "input"}),
            "chapter": forms.TextInput(attrs={"class": "input"}),
            "topic": forms.TextInput(attrs={"class": "input"}),
            "trap": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }
