from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI

def index(request):
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    # Access the API key from the environment
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    """
    チャット画面
    """

    # 応答結果
    chat_results = ""

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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "日本語で応答してください"
                    },
                    {
                        "role": "user",
                        "content": sentence
                    },
                ],
            )

            chat_results = response.choices[0].message.content

    else:
        form = ChatForm()

    template = loader.get_template('chat_app/index.html')
    context = {
        'form': form,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
