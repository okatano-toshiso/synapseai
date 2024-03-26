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
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """
                            Translate the given English prompt into Japanese. If there are characters other than English, please respond in Japanese by saying "Please fill in English only."
                            I will write the rules below
                            1. Please translate into Japanese line by line.
                            2. Please also leave the original text for translation.
                            3. Please write the translated Japanese on the next line after the translation source.
                            4. Pause one line and then translate the next line
                            Repeat the above rules until the end.
                            Please respond only in the original and translated Japanese.
                        """
                    },
                    {
                        "role": "user",
                        "content": sentence
                    },
                ],
                temperature=0
            )
            chat_results = response.choices[0].message.content
    else:
        form = ChatForm()

    chat_results = chat_results.replace("\n", "<br>")
    domain = request.build_absolute_uri('/')
    template = loader.get_template('lyric_trans/index.html')
    context = {
        'form': form,
        'domain': domain,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
