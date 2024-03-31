from django import forms

class ChatForm(forms.Form):

    CHOICES = [
        ('black', '黒'),
        ('white', '白'),
        ('green', '緑'),
        ('red', '赤'),
        ('deep blue', '藍'),
        ('aqua', 'アクア'),
    ]
    color = forms.ChoiceField(label='色', choices=CHOICES, required=True)
    CHOICES = [
        ('black', '黒'),
        ('white', '白'),
        ('green', '緑'),
        ('red', '赤'),
        ('deep blue', '藍'),
        ('aqua', 'アクア'),
    ]
    background = forms.ChoiceField(label='背景色', choices=CHOICES, required=True)
    image = forms.CharField(label='イメージ', required=False)
