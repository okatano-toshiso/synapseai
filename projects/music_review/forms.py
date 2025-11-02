from django import forms

class ChatForm(forms.Form):
    MODEL_CHOICES = [
        ('gpt-5', 'GPT-5'),
        ('o1', 'o1'),
        ('o1-preview', 'o1 Preview'),
        ('o1-mini', 'o1 Mini'),
        ('gpt-4.1', 'GPT-4.1'),
        ('gpt-4.1-mini', 'GPT-4.1 Mini'),
        ('gpt-4o', 'GPT-4o'),
        ('gpt-4o-mini', 'GPT-4o Mini'),
        ('gpt-4-turbo', 'GPT-4 Turbo'),
        ('gpt-4', 'GPT-4'),
        ('gpt-3.5-turbo', 'GPT-3.5 Turbo'),
    ]
    
    model = forms.ChoiceField(
        label='MODEL',
        choices=MODEL_CHOICES,
        initial='gpt-5',
        widget=forms.Select(attrs={'class': 'model-select'}),
        required=True
    )
    title = forms.CharField(label='TITLE', widget=forms.TextInput(), required=False)
    artist = forms.CharField(label='ARTIST', widget=forms.TextInput(), required=False)
    comment = forms.CharField(label='COMMENT',widget=forms.Textarea(attrs={'placeholder': 'review'}),required=False)
    recommend = forms.CharField(label='RECOMMEND', widget=forms.TextInput(), required=False)
    wiki_discography = forms.CharField(label='WIKI_DISC', widget=forms.TextInput(), required=False)
    no_data = forms.BooleanField(label='NO DATA', required=False)
    release_date = forms.DateField(
        label='RELEASE',
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False,
        input_formats=['%Y/%m/%d', '%Y-%m-%d']
    )
    label = forms.CharField(label='LABEL', widget=forms.TextInput(), required=False)
    producer_name = forms.CharField(label='PRODUCER', widget=forms.TextInput(), required=False)
    wiki_biography = forms.CharField(label='WIKI_BIO', widget=forms.TextInput(), required=False)
    source1 = forms.CharField(label='SOURCE1', widget=forms.TextInput(), required=False)
    source2 = forms.CharField(label='SOURCE2', widget=forms.TextInput(), required=False)
    spotyfi = forms.CharField(label='SPOTYFI', widget=forms.TextInput(), required=False)
    youtube = forms.CharField(label='YOUTUBE', widget=forms.TextInput(), required=False)
