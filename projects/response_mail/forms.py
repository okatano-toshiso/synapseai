from django import forms

class ChatForm(forms.Form):
    company = forms.CharField(label='会社', widget=forms.TextInput(), required=False)
    name = forms.CharField(label='名前', widget=forms.TextInput(), required=False)
    received_mail= forms.CharField(
        label='受信メール',
        widget=forms.Textarea(attrs={'placeholder': 'ここに受信メールの内容を入力してください 個人情報を入力しないでください'}),
        required=True
    )
    response_mail = forms.CharField(
        label='返信メール',
        widget=forms.Textarea(attrs={'placeholder': 'ここに返信メッセージを入力してください 個人情報を入力しないでください'}),
        required=True
    )
