from django import forms


class MusicSearchForm(forms.Form):
    LANGUAGE_CHOICES = [
        ('ja', '邦楽（日本語Wikipedia）'),
        ('en', '洋楽（英語Wikipedia）'),
    ]
    
    language = forms.ChoiceField(
        label='ジャンル',
        choices=LANGUAGE_CHOICES,
        initial='ja',
        widget=forms.RadioSelect(attrs={'class': 'language-radio'}),
        required=True
    )
    
    artist_name = forms.CharField(
        label='アーティスト名',
        widget=forms.TextInput(attrs={
            'class': 'artist-input',
            'placeholder': 'アーティスト名を入力してください'
        }),
        required=True,
        max_length=200
    )
    
    album_name = forms.CharField(
        label='アルバム名（任意）',
        widget=forms.TextInput(attrs={
            'class': 'album-input',
            'placeholder': 'アルバム名を入力してください（任意）'
        }),
        required=False,
        max_length=200
    )
