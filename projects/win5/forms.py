from django import forms

class ChatForm(forms.Form):
    date = forms.DateField(
        label='レース日時',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    location_01 = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number_01 =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder': 'レース番号', 'class': 'racehorse-frame'}), required=False)
    location_02 = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number_02 =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder':'レース番号', 'class': 'racehorse-frame'}), required=False)
    location_03 = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number_03 =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder':'レース番号', 'class': 'racehorse-frame'}), required=False)
    location_04 = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number_04 =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder':'レース番号', 'class': 'racehorse-frame'}), required=False)
    location_05 = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number_05 =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder':'レース番号', 'class': 'racehorse-frame'}), required=False)


