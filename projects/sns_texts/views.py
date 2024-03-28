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
                        "role": "user",
                        "content": "ここに新しいユーザーの入力を置く"
                    },
                    {
                        "role": "system",
                        "content": """
                        下記規則に従って文章を書き直してください。
                        ・日本語で応答してください。
                        ・140文字以内に書き直してください。
                        ・差別的な表現があったら書き直してください。
                        ・不適切な表現があったら書き直してください。
                        ・暴力的な表現があれば削除してください。
                        ・性的な表現があれば削除してください。
                        ・できるだけ丁寧な言葉遣いに書き直してください。
                        そして書き直した文章だけ回答してください。説明などは一切しないでください。
                        なおした文章だけを返してください。
                        """
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

    domain = request.build_absolute_uri('/')
    template = loader.get_template('sns_texts/index.html')
    context = {
        'form': form,
        'domain': domain,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
