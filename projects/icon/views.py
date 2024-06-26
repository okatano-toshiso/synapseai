from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
import requests
import json
import deepl

@login_required
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
    image_url = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            color = form.cleaned_data['color']
            background = form.cleaned_data['background']
            image = form.cleaned_data['image']
            try:
                def translate_text(text, auth_key, source_lang, target_lang):
                    translator = deepl.Translator(auth_key)
                    result = translator.translate_text(text, source_lang = source_lang, target_lang = target_lang)
                    return result.text
                image = translate_text(image, API_KEY, 'JA', 'EN-GB')

                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                response =  client.images.generate(
                    model   = "dall-e-3",
                    prompt = f"""Design a pictogram-style app icon, using only two HEX color codes: ‘{color}’ for the icon itself and ‘{background}’ for the background. The theme is based around {image}, and the icon should feature a single, central symbolic element related to {image}. The design must strictly adhere to using only these two specified colors, creating a clear and simple two-tone image that effectively communicates the theme.No drop shadow and no gradient.""",
                    size="1024x1024"
                )
                image_url = response.data[0].url
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('icon/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': "icon",
        'img_results': image_url
    }
    return HttpResponse(template.render(context, request))
