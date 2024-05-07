from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
import requests
import json
import deepl

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    except KeyError:
        return HttpResponse("OPENAI_API_APIキーが設定されていません。", status=500)
    try:
        API_KEY = os.environ['DEEPL_API_KEY']
    except KeyError:
        return HttpResponse("DEEPL_APIキーが設定されていません。", status=500)
    translator = ""
    english_result = ""
    japanese_result = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            category = form.cleaned_data['category']
            details = form.cleaned_data['texts']
            try:
                def translate_text(text, auth_key, source_lang, target_lang):
                    translator = deepl.Translator(auth_key)
                    result = translator.translate_text(text, source_lang = source_lang, target_lang = target_lang)
                    return result.text
                details = translate_text(details, API_KEY, 'JA', 'EN-GB')
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            You are a historian.
                            What are some sayings of famous people from the past and present and what is the name of the famous person?
                            category is {category} And about {details}
                            Please pick three aphorisms.
                            Please output in the form of ' aphorisms <br /> by speaker '.
                            """
                        },
                    ],
                )
                english_result = response.choices[0].message.content
                japanese_result = translate_text(english_result, API_KEY, 'EN', 'JA')
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('aphorism/index.html')
    english_result = english_result.replace("\n", "<br>")
    japanese_result = japanese_result.replace("\n", "<br>")
    context = {
        'form': form,
        'domain': domain,
        'app_name': "aphorism",
        'english_result': english_result,
        'japanese_result': japanese_result
    }
    return HttpResponse(template.render(context, request))
