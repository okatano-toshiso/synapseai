from django import forms

class ChatForm(forms.Form):
    title = forms.CharField(label='TITLE', widget=forms.TextInput(), required=False)
    artist = forms.CharField(label='ARTIST', widget=forms.TextInput(), required=False)
    comment = forms.CharField(label='COMMENT',widget=forms.Textarea(attrs={'placeholder': 'review'}),required=False)
    recommend = forms.CharField(label='RECOMMEND', widget=forms.TextInput(), required=False)
    wiki_discography = forms.CharField(label='WIKI_DISC', widget=forms.TextInput(), required=False)
    wiki_biography = forms.CharField(label='WIKI_BIO', widget=forms.TextInput(), required=False)
    source1 = forms.CharField(label='SOURCE1', widget=forms.TextInput(), required=False)
    source2 = forms.CharField(label='SOURCE2', widget=forms.TextInput(), required=False)
    spotyfi = forms.CharField(label='SPOTYFI', widget=forms.TextInput(), required=False)
    youtube = forms.CharField(label='YOUTUBE', widget=forms.TextInput(), required=False)
