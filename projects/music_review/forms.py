from django import forms

class ChatForm(forms.Form):
    official_site_discography = forms.CharField(label='OFFICIAL_SITE_DISCOGRAPHY', widget=forms.TextInput(), required=False)
    official_site_biography = forms.CharField(label='OFFICIAL_SITE_BIOGRAPHY', widget=forms.TextInput(), required=False)
    wiki_discography = forms.CharField(label='WIKI_DISCOGRAPHY', widget=forms.TextInput(), required=False)
    wiki_biography = forms.CharField(label='WIKI_BIOGRAPHY', widget=forms.TextInput(), required=False)
    spotyfi = forms.CharField(label='SPOTYFI', widget=forms.TextInput(), required=False)
    youtube = forms.CharField(label='YOUTUBE', widget=forms.TextInput(), required=False)
    recommend = forms.CharField(label='RECOMMEND_TRACK', widget=forms.TextInput(), required=False)
