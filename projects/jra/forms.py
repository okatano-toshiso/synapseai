from django import forms

class ChatForm(forms.Form):
    rase = forms.CharField(label='レース名', widget=forms.TextInput(), required=False)
    date = forms.DateField(
        label='レース日時',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    distance = forms.IntegerField(label='距離', widget=forms.NumberInput(attrs={'min': 0, 'max': 9999}), required=False)
    CHOICES = [
        ('turf', '芝'),
        ('dirt', 'ダート'),
        ('obstacles', '障害物'),
    ]
    course = forms.ChoiceField(label='コース', choices=CHOICES, required=True)
    CHOICES = [
        ('left', '左回り'),
        ('right', '右回り')
    ]
    orientation = forms.ChoiceField(label='コース', choices=CHOICES, required=True)
    place = forms.CharField(label='競馬場', widget=forms.TextInput(), required=False)
    CHOICES = [
        ('fine', '晴れ'),
        ('cloudiness', '曇り'),
        ('rain', '雨'),
    ]
    weather = forms.ChoiceField(label='天候', choices=CHOICES, required=True)
    CHOICES = [
        ('good', '良'),
        ('semi-heavy', '稍重'),
        ('heavy', '重'),
        ('poor', '不良'),
    ]
    condition = forms.ChoiceField(label='馬場状態', choices=CHOICES, required=True)
    CHOICES = [
        ('exacta', '単勝'),
        ('place', '複勝'),
        ('bracket_quinella', '枠連'),
        ('quinella', '馬連'),
        ('quinella_place', 'ワイド'),
        ('tierce', '3連複'),
        ('trio', '3連単'),
    ]
    betting = forms.ChoiceField(label='馬券の種類', choices=CHOICES, required=True)

    for i in range(1, 19):
        num = str(i).zfill(2)  # 01, 02, ..., 18 のように0埋め
        locals()[f'Racehorse_frame_{num}'] = forms.IntegerField(label=f'枠番号 {num}', widget=forms.NumberInput(attrs={'min': 1, 'max': 19, 'placeholder': f'枠 {num}', 'class': 'racehorse-frame'}), required=False)
        locals()[f'Racehorse_number_{num}'] = forms.IntegerField(label=f'馬番 {num}', widget=forms.NumberInput(attrs={'min': 1, 'max': 19, 'placeholder': f'番 {num}', 'class': 'racehorse-number'}), required=False)
        locals()[f'Racehorse_name_{num}'] = forms.CharField(label=f'馬名 {num}', widget=forms.TextInput(attrs={'placeholder': f'馬名 {num}', 'class': 'racehorse-name'}), required=False)
        GENDER_CHOICES = [('牡', '牡'), ('牝', '牝'), ('セン', 'セン')]
        locals()[f'Racehorse_gender_{num}'] = forms.ChoiceField(label=f'性別 {num}', choices=GENDER_CHOICES, widget=forms.Select(attrs={'class': 'racehorse-gender'}), required=False)
        locals()[f'Racehorse_age_{num}'] = forms.IntegerField(label=f'年齢 {num}', widget=forms.NumberInput(attrs={'min': 1, 'max': 12, 'placeholder': f'齢 {num}', 'class': 'racehorse-age'}), required=False)
        locals()[f'Racehorse_jockey_{num}'] = forms.CharField(label=f'騎手 {num}', widget=forms.TextInput(attrs={'placeholder': f'騎手 {num}', 'class': 'racehorse-jockey'}), required=False)
        locals()[f'Racehorse_weight_{num}'] = forms.DecimalField(label=f'重量 {num}', widget=forms.NumberInput(attrs={'step': 0.1, 'placeholder': f'重 {num}', 'class': 'racehorse-weight'}), required=False, max_digits=4, decimal_places=1)
        locals()[f'Racehorse_barn_{num}'] = forms.CharField(label=f'厩舎 {num}', widget=forms.TextInput(attrs={'placeholder': f'厩 {num}', 'class': 'racehorse-barn'}), required=False)
        locals()[f'Racehorse_body_{num}'] = forms.IntegerField(label=f'馬体重 {num}', widget=forms.NumberInput(attrs={'min': 0, 'max': 999, 'placeholder': f'体重 {num}', 'class': 'racehorse-body'}), required=False)
        locals()[f'Racehorse_fluctuation_{num}'] = forms.IntegerField(label=f'馬体重変動 {num}', widget=forms.NumberInput(attrs={'min': -99, 'max': 99, 'placeholder': f'変動 {num}', 'class': 'racehorse-fluctuation'}), required=False)
        locals()[f'Racehorse_odds_{num}'] = forms.DecimalField(label=f'オッズ {num}', widget=forms.NumberInput(attrs={'step': 0.1, 'placeholder': f'オッズ {num}', 'class': 'racehorse-odds'}), required=False, max_digits=4, decimal_places=1)


