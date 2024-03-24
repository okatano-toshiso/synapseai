from django import forms
from .models import DemoImage

class ChatForm(forms.Form):

    # sentence = forms.CharField(label='', widget=forms.Textarea(), required=True)
    # class Meta:
    #         model = MyModel
    #         fields = ['image']

# class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = DemoImage
        fields = ['image']