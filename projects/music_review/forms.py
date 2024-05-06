from django import forms

class ChatForm(forms.Form):
    title = forms.CharField(label='アルバム名', widget=forms.TextInput(), required=False)
    artist = forms.CharField(label='アーティスト', widget=forms.TextInput(), required=False)
    producer = forms.CharField(label='プロデューサー', widget=forms.TextInput(), required=False)
    genre = forms.CharField(label='ジャンル', widget=forms.TextInput(), required=False)
    label = forms.CharField(label='レーベル', widget=forms.TextInput(), required=False)
    release = forms.DateField(
        label='リリース日',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    review = forms.CharField(
        label='評論',
        widget=forms.Textarea(attrs={'placeholder': 'レビュー'}),
        required=True
    )
    recommend = forms.CharField(label='おすすめ', widget=forms.TextInput(), required=False)
    track_list = forms.CharField(
        label='収録曲',
        widget=forms.Textarea(attrs={'placeholder': '収録曲'}),
        required=True
    )
    members = forms.CharField(
        label='参加者',
        widget=forms.Textarea(attrs={'placeholder': '参加メンバー'}),
        required=False
    )
