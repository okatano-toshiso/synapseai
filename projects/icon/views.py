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
    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    API_KEY = os.environ['DEEPL_API_KEY']
    translator = ""
    image_url = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            color = form.cleaned_data['color']
            background = form.cleaned_data['background']
            image = form.cleaned_data['image']
            def translate_text(text, auth_key):
                translator = deepl.Translator(auth_key)
                result = translator.translate_text(text, target_lang="JA")
                return result.text
            image = translate_text(image, API_KEY)
            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            response =  client.images.generate(
                model   = "dall-e-3",
                prompt = f"""Design a pictogram-style app icon, using only two HEX color codes: ‘{color}’ for the icon itself and ‘{background}’ for the background. The theme is based around {image}, and the icon should feature a single, central symbolic element related to {image}. The design must strictly adhere to using only these two specified colors, creating a clear and simple two-tone image that effectively communicates the theme.No drop shadow and no gradient.""",
                size="1024x1024"
            )
            image_url = response.data[0].url
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
