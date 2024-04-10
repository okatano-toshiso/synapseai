from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI

def index(request):
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            name = form.cleaned_data['name']
            purpose = form.cleaned_data['purpose']
            relation = form.cleaned_data['relation']
            greeting = form.cleaned_data['greeting']
            number = form.cleaned_data['number']
            message = form.cleaned_data['message']
            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "ここに新しいユーザーの入力を置く"
                    },
                    {
                        "role": "system",
                        "content": f"""
                        常に新しいユーザーです。履歴は忘れてください。
                        名前も会社名も忘れてください。
                        あなたは日本語が詳しい優秀な校正編集者です。
                        このメールの目的は‘{purpose}’です。
                        このメールの送り先の相手は‘{purpose}’です。
                        このメールには挨拶は‘{greeting}’です。
                        このメールを送る相手の人数は‘{number}’です。
                        下記のテキストが元になる送信テキストです。

                        送信テキスト
                        ーーーーーーーーーーーーーーーーーーーーーー
                        ‘{message}‘
                        ーーーーーーーーーーーーーーーーーーーーーー
                        上記のテキストを丁寧にわかりやすくなるように日本語で校正してください。
                        必ずメール文章の構成をキープしてください。
                        説明などは不要ですので、校正した文章のみをレスポンスしてください。
                        """
                    }
                ],
            )
            chat_results = response.choices[0].message.content
            chat_results = chat_results.replace("\n", "<br>")
            chat_results = company + "<br>" + name + "<br><br>" + chat_results

    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('send_mail/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
