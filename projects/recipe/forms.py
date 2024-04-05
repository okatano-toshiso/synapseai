from django import forms
from .models import DemoImage

class ChatForm(forms.Form):

# class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = DemoImage
        fields = ['image']