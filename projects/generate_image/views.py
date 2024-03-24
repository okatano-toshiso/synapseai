from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
import requests
import json

def index(request):
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # Access the API key from the environment
    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    """
    生成AI画像作成画面
    """

    # 応答結果
    image_url = ""

    if request.method == "POST":
        # ChatGPTボタン押下時

        form = ChatForm(request.POST)
        if form.is_valid():

            sentence = form.cleaned_data['sentence']

            # TODO: APIキーのハードコーディングは避ける
            # openai.api_key = "APIキー"
            client = OpenAI(
                # This is the default and can be omitted
                api_key = OPENAI_API_KEY,
            )
            # ChatGPT
            response =  client.images.generate(
                model   = "dall-e-3",   # モデル  
                prompt  = sentence,         # 画像生成に用いる説明文章         
                n       = 1,            # 何枚の画像を生成するか  
                size="1024x1024"        # 画像サイズ
            )

            # API応答から画像URLを指定
            image_url = response.data[0].url
            # 画像をローカルに保存
            # img_response = requests.get(image_url)
            # image_path = '/static/img/chat-gpt-generated-image.jpg'

    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('gene_img/index.html')
    context = {
        'form': form,
        'domain': domain,
        'img_results': image_url
    }
    return HttpResponse(template.render(context, request))
