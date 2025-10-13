from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
from pathlib import Path

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
            model = form.cleaned_data['model']
            purpose = form.cleaned_data['purpose']
            relation = form.cleaned_data['relation']
            greeting = form.cleaned_data['greeting']
            number = form.cleaned_data['number']
            message = form.cleaned_data['message']
            try:
                # プロンプトファイルを読み込む
                prompt_file = Path(__file__).parent / 'prompts' / 'system_prompt.txt'
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    system_prompt_template = f.read()
                
                # プロンプトに変数を埋め込む
                system_prompt = system_prompt_template.format(
                    purpose=purpose,
                    relation=relation,
                    greeting=greeting,
                    number=number,
                    message=message
                )
                
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": "ここに新しいユーザーの入力を置く"
                        },
                        {
                            "role": "system",
                            "content": system_prompt
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
    template = loader.get_template('send_mail/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
