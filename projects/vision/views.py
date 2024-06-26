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

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    domain = request.build_absolute_uri('/')
    file_path = 'demo.jpg'
    if default_storage.exists(file_path):
        default_storage.delete(file_path)
    img_results = ""
    image_path = ""
    if request.method == "POST":
        form = ChatForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image']
            image_content = image_file.read()
            default_storage.save('demo.jpg', ContentFile(image_content))
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                image_path = settings.BASE_DIR / "uploads/demo.jpg"
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
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    template = loader.get_template('vision/index.html')
    context = {
        'form': form,
        'domain': domain,
        'image_path' : image_path,
        'img_results': img_results
    }
    return HttpResponse(template.render(context, request))
