from django import forms

class ChatForm(forms.Form):
    title = forms.CharField(label='TITLE', widget=forms.TextInput(), required=False)
    artist = forms.CharField(label='ARTIST', widget=forms.TextInput(), required=False)
    producer = forms.CharField(label='PRODUCER', widget=forms.TextInput(), required=False)
    genre = forms.CharField(label='GENRE', widget=forms.TextInput(), required=False)
    label = forms.CharField(label='LABEL', widget=forms.TextInput(), required=False)
    release = forms.DateField(
        label='RELEASE',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    spotyfi = forms.CharField(label='SPOTYFI', widget=forms.TextInput(), required=False)
    youtube = forms.CharField(label='YOUTUBE', widget=forms.TextInput(), required=False)
    biography = forms.CharField(
        label='BIOGRAPHY',
        widget=forms.Textarea(attrs={'placeholder': 'BIOGRAPHY'}),
        required=True
    )
    review = forms.CharField(
        label='REVIEW',
        widget=forms.Textarea(attrs={'placeholder': 'REVIEW'}),
        required=True
    )
    recommend = forms.CharField(label='RECOMMEND', widget=forms.TextInput(), required=False)
    track_list = forms.CharField(
        label='TRACKLISTS',
        widget=forms.Textarea(attrs={'placeholder': 'TRACKLISTS'}),
        required=True
    )
    members = forms.CharField(
        label='PERSONAL',
        widget=forms.Textarea(attrs={'placeholder': 'PERSONAL'}),
        required=False
    )
