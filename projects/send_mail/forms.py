from django import forms

class ChatForm(forms.Form):
    company = forms.CharField(label='会社', widget=forms.TextInput(), required=False)
    name = forms.CharField(label='名前', widget=forms.TextInput(), required=False)
    CHOICES1 = [
        ('営業', '営業'),
        ('採用', '採用'),
        ('遊びの誘い', '遊びの誘い'),
        ('久々のメール', '久々のメール')
    ]
    purpose = forms.ChoiceField(label='目的', choices=CHOICES1, required=True)
    CHOICES2 = [
        ('年長者・上司・顧客', '年長者・上司・顧客'),
        ('同僚','同僚'),
        ('友達', '友達'),
        ('家族', '家族'),
        ('知人', '知人'),
        ('初めてメールする人', '初めてメールする人')
    ]
    relation = forms.ChoiceField(label='関係', choices=CHOICES2, required=True)
    CHOICES3 = [
        ('不要', '不要'),
        ('年始', '年始'),
        ('新年度', '新年度'),
        ('春', '春'),
        ('夏', '夏'),
        ('秋', '秋'),
        ('冬', '冬')
    ]
    greeting = forms.ChoiceField(label='挨拶', choices=CHOICES3, required=True)
    CHOICES4 = [
        ('1人', '1人'),
        ('2人以上','2人以上')
    ]
    number = forms.ChoiceField(label='人数', choices=CHOICES4, required=True)
    message = forms.CharField(label='平文', widget=forms.Textarea(), required=True)