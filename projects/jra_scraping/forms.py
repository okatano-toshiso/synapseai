from django import forms

class ChatForm(forms.Form):
    race = forms.CharField(label='スクレイピング', widget=forms.HiddenInput(), required=False, initial='True')