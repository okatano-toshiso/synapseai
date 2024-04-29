from django import forms

class ChatForm(forms.Form):
    title = forms.CharField(label='作品名', widget=forms.TextInput(), required=False)
    author = forms.CharField(label='著者', widget=forms.TextInput(), required=False)
    publisher = forms.CharField(label='出版社', widget=forms.TextInput(), required=False)
    release = forms.DateField(
        label='発行日',
        widget=forms.DateInput(attrs={'type': 'date'}),  # ブラウザの日付選択ウィジェットを使用
        required=False
    )
    introduction = forms.CharField(
        label='導入部',
        widget=forms.Textarea(attrs={'placeholder': '読んだ本のタイトルと著者名を紹介します。本を読むことにした動機や、興味を持った理由を簡潔に述べます。'}),
        required=True
    )
    summary = forms.CharField(
        label='内容の要約',
        widget=forms.Textarea(attrs={'placeholder': '主要な登場人物、設定、ストーリーの流れを簡潔に要約します。本の中で特に印象に残った場面やテーマについて触れることができます。'}),
        required=True
    )
    impressions = forms.CharField(
        label='感想・考察',
        widget=forms.Textarea(attrs={'placeholder': '物語から何を感じ取ったか、どのような考えを持ったかを述べます。物語のテーマやメッセージが自分の人生にどのように関連するかを書きます。'}),
        required=True
    )
    conclusion = forms.CharField(
        label='結論',
        widget=forms.Textarea(attrs={'placeholder': '本全体を通して得られた教訓や感じたことのまとめ。他の読者にこの本をおすすめするかどうか、その理由を含めます。'}),
        required=True
    )
