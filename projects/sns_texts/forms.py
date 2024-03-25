from django import forms

class ChatForm(forms.Form):

    sentence = forms.CharField(label='', widget=forms.Textarea(), required=True)
