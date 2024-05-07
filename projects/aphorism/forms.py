from django import forms

class ChatForm(forms.Form):
    CHOICES = [
        ('business', 'ビジネス'),
        ('work', '仕事'),
        ('history', '歴史'),
        ('sports', 'スポーツ'),
        ('education', '教育'),
        ('relationships', '人間関係'),
        ('time', '時間'),
        ('efficiency', '効率'),
        ('romance', '恋愛'),
        ('life', '人生'),
        ('dreams', '夢'),
        ('music', '音楽'),
        ('future', '将来'),
        ('health', '健康'),
        ('war', '戦争'),
        ('comics', '漫画'),
        ('politics', '政治'),
    ]
    category = forms.ChoiceField(label='カテゴリー', choices=CHOICES, required=True)
    texts = forms.CharField(label='そのほか', required=False)
