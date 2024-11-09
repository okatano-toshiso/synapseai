from django import forms

class ChatForm(forms.Form):
    official_site_discography = forms.CharField(label='DISCOGRAPHY', widget=forms.TextInput(), required=False)
    official_site_biography = forms.CharField(label='BIOGRAPHY', widget=forms.TextInput(), required=False)
    wiki_discography = forms.CharField(label='WIKI_DISC', widget=forms.TextInput(), required=False)
    wiki_biography = forms.CharField(label='WIKI_BIO', widget=forms.TextInput(), required=False)
    spotyfi = forms.CharField(label='SPOTYFI', widget=forms.TextInput(), required=False)
    youtube = forms.CharField(label='YOUTUBE', widget=forms.TextInput(), required=False)
    recommend = forms.CharField(label='RECOMMEND', widget=forms.TextInput(), required=False)
