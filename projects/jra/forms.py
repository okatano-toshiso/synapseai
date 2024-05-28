from django import forms
from .models import RaceInfo

class ChatForm(forms.ModelForm):
    rase = forms.CharField(label='レース名', widget=forms.TextInput(), required=False)
    date = forms.DateField(
        label='レース日時',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    distance = forms.IntegerField(label='距離', widget=forms.NumberInput(attrs={'min': 0, 'max': 9999}), required=False)
    CHOICES = [
        ('芝', '芝'),
        ('ダート', 'ダート'),
        ('障害物', '障害物'),
    ]
    course = forms.ChoiceField(label='コース', choices=CHOICES, required=True)
    CHOICES = [
        ('左回り', '左回り'),
        ('右回り', '右回り')
    ]
    orientation = forms.ChoiceField(label='回り', choices=CHOICES, required=True)
    CHOICES = [
        ('札幌競馬場', '札幌競馬場'),
        ('函館競馬場', '函館競馬場'),
        ('福島競馬場', '福島競馬場'),
        ('中山競馬場', '中山競馬場'),
        ('東京競馬場', '東京競馬場'),
        ('新潟競馬場', '新潟競馬場'),
        ('中京競馬場', '中京競馬場'),
        ('京都競馬場', '京都競馬場'),
        ('阪神競馬場', '阪神競馬場'),
        ('小倉競馬場', '小倉競馬場')
    ]
    place = forms.ChoiceField(label='中央競馬', choices=CHOICES, required=True)
    CHOICES = [
        ('晴れ', '晴れ'),
        ('曇り', '曇り'),
        ('雨', '雨'),
    ]
    weather = forms.ChoiceField(label='天候', choices=CHOICES, required=True)
    CHOICES = [
        ('良', '良'),
        ('稍重', '稍重'),
        ('重', '重'),
        ('不良', '不良'),
    ]
    condition = forms.ChoiceField(label='馬場状態', choices=CHOICES, required=True)
    CHOICES = [
        ('単勝', '単勝'),
        ('複勝', '複勝'),
        ('枠連', '枠連'),
        ('馬連', '馬連'),
        ('ワイド', 'ワイド'),
        ('3連複', '3連複'),
        ('3連単', '3連単'),
    ]
    betting = forms.ChoiceField(label='馬券の種類', choices=CHOICES, required=True)
    location = forms.CharField(label='開催場所', widget=forms.TextInput(), required=False)
    race_number =forms.IntegerField(label='レース番号', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder': 'レース番号', 'class': 'racehorse-frame'}), required=False)

    class Meta:
        model = RaceInfo
        fields = ['csv_file']
