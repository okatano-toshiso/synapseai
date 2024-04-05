from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
import requests
import base64
import json
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import deepl


def index(request):
    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    DEEPL_API_KEY = os.environ['DEEPL_API_KEY']
    domain = request.build_absolute_uri('/')
    file_path = 'recipe.jpg'
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
    img_results = ""
    recipe_results = ""
    image_path = ""
    if request.method == "POST":
        form = ChatForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            image_content = image_file.read()
            default_storage.save('recipe.jpg', ContentFile(image_content))
            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            image_path = settings.BASE_DIR / "uploads/recipe.jpg"
            print(image_path)
            def encode_image(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            base64_image = encode_image(image_path)
            headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                "role": "user",
                "content": [
                    {
                    "type": "text",
                    "text": """
                        What’s in this image?
                        Just tell me the name of the vegetable in the image.
                        Please do not answer except for the name of the vegetable.
                        If there are no vegetables in the picture, please return the message No vegetables.
                        """
                    },
                    {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                    }
                ]
                }
            ],
            "max_tokens": 300
            }
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            img_results = (response.json().get("choices")[0]["message"]["content"])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are a cookery researcher.
                            USER gives you an ingredient.
                            Please give us a recipe that can be cooked from that ingredient.
                        """
                    },
                    {
                        "role": "user",
                        "content": "Cooking ingredients" + img_results
                    },
                ],
            )
            recipe_results = response.choices[0].message.content

            def translate_text_with_deepl(text, auth_key):
                translator = deepl.Translator(auth_key)
                result = translator.translate_text(text, target_lang="JA")
                return result.text
            recipe_results = translate_text_with_deepl(recipe_results, DEEPL_API_KEY)
            recipe_results = recipe_results.replace("\n", "<br />")
            img_results = translate_text_with_deepl(img_results, DEEPL_API_KEY)

    else:
        form = ChatForm()
    template = loader.get_template('recipe/index.html')
    context = {
        'form': form,
        'domain': domain,
        'image_path' : image_path,
        'img_results': img_results,
        'recipe_results': recipe_results,
    }
    return HttpResponse(template.render(context, request))
