from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            company = form.cleaned_data['company']
            name = form.cleaned_data['name']
            received_mail = form.cleaned_data['received_mail']
            response_mail = form.cleaned_data['response_mail']
            try:
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

                            受信メッセージ
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {received_mail}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            メールから受信したメッセージです。内容を把握してください。

                            返信メッセージ
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {response_mail}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            受信メッセージの内容を把握した上で、返信メッセージのテキストを丁寧にわかりやすくなるように日本語で校正してください。
                            必ずメール文章の構成をキープしてください。
                            説明などは不要ですので、校正した文章のみをレスポンスしてください。
                            """
                        }
                    ],
                )
                chat_results = response.choices[0].message.content
                chat_results = chat_results.replace("\n", "<br>")
                chat_results = company + "<br>" + name + "<br><br>" + chat_results
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('response_mail/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
