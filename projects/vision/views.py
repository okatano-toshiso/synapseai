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


def index(request):

    # Access the API key from the environment
    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']

    """
    生成AI画像解析
    """

    file_path = 'demo.jpg'
    if default_storage.exists(file_path):
        default_storage.delete(file_path)

    # 応答結果
    img_results = ""
    image_path = ""

    if request.method == "POST":
        form = ChatForm(request.POST, request.FILES)
        if form.is_valid():

            image_file = request.FILES['image']
            image_content = image_file.read()
            default_storage.save('demo.jpg', ContentFile(image_content))

            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            def encode_image(image_path):
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode('utf-8')
            image_path = "uploads/demo.jpg"
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
                    "text": "What’s in this image?　日本語で答えてください"
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

    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('vision/index.html')
    context = {
        'form': form,
        'domain': domain,
        'image_path' : image_path,
        'img_results': img_results
    }
    return HttpResponse(template.render(context, request))
