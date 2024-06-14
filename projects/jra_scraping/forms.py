from django import forms

class ChatForm(forms.Form):
    date = forms.DateField(
        label='レース日時',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    location = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder': 'レース番号', 'class': 'racehorse-frame'}), required=False)
    race = forms.CharField(label='スクレイピング', widget=forms.HiddenInput(), required=False, initial='True')
