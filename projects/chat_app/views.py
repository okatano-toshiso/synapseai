from django.shortcuts import render
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
            try:
                sentence = form.cleaned_data['sentence']
            except Exception as e:
                return HttpResponse("フォームが取得できませんでした", status=400)
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                selected_model = request.POST.get("model", "gpt-5")
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "日本語で応答してください。"
                        },
                        {
                            "role": "user",
                            "content": sentence
                        },
                    ],
                )
                chat_results = response.choices[0].message.content
                chat_results = chat_results.lstrip()
                chat_results = chat_results.replace("\n", "<br>")
                chat_results += f" （{selected_model}）"
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('chat_app/index.html')
    context = {
        'form': form,
        'domain': domain,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
