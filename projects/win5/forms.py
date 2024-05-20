from django import forms

class ChatForm(forms.Form):
    date = forms.DateField(
        label='レース日時',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    rase01 = forms.CharField(label='レース1', widget=forms.TextInput(), required=False)
    rase02 = forms.CharField(label='レース2', widget=forms.TextInput(), required=False)
    rase03 = forms.CharField(label='レース3', widget=forms.TextInput(), required=False)
    rase04 = forms.CharField(label='レース4', widget=forms.TextInput(), required=False)
    rase05 = forms.CharField(label='レース5', widget=forms.TextInput(), required=False)


