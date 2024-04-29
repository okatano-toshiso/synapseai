from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import deepl
import os
from openai import OpenAI
import requests
import json

@login_required
def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    except KeyError:
        return HttpResponse("OPENAIのAPIキーが設定されていません。", status=500)
    try:
        DEEPL_API_KEY = os.environ['DEEPL_API_KEY']
    except KeyError:
        return HttpResponse("DEEPLのAPIキーが設定されていません。", status=500)
    image_url = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            try:
                initial_message = 'I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:'
                sentence = form.cleaned_data['sentence']
                def translate_text_with_deepl(text, auth_key):
                    translator = deepl.Translator(auth_key)
                    result = translator.translate_text(text, target_lang="EN-US")
                    return result.text
                sentence = translate_text_with_deepl(sentence, DEEPL_API_KEY)
                sentence = initial_message + sentence
                print(sentence)
            except Exception as e:
                return HttpResponse(f"DEEPL_APIのAPI呼び出し中にエラーが発生しました: {str(e)}", status=500)
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                response =  client.images.generate(
                    model   = "dall-e-3",
                    prompt  = sentence,
                    n       = 1,
                    size="1024x1024",
                )
                image_url = response.data[0].url
                print(response.data)
            except Exception as e:
                return HttpResponse(f"OPENAI_APIのAPI呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('gene_img/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': "generate_image",
        'img_results': image_url
    }
    return HttpResponse(template.render(context, request))
