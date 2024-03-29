from django import forms

class TtsForm(forms.Form):

    sentence = forms.CharField(label='', widget=forms.Textarea(), required=True)
