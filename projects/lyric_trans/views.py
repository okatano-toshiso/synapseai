from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import deepl
import os

def index(request):

    API_KEY = os.environ['DEEPL_API_KEY']

    trans_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            if len(sentence) < 2001:
                def translate_text_with_deepl(text, auth_key):
                    translator = deepl.Translator(auth_key)
                    result = translator.translate_text(text, target_lang="JA")
                    return result.text

                def get_translated_texts():
                    auth_key = API_KEY
                    original_texts = sentence
                    lines = original_texts.strip().split('\n')
                    translated_texts = []
                    for line in lines:
                        translated_line = translate_text_with_deepl(line, auth_key)
                        translated_texts.append(f'{line}\n{translated_line}\n')
                    return translated_texts

                results = get_translated_texts()
                for result in results:
                    trans_results += result + "\n"
            else:
                trans_results = '文字数オーバーです'
    else:
        form = ChatForm()

    trans_results = trans_results.replace("\n", "<br>")
    domain = request.build_absolute_uri('/')
    template = loader.get_template('lyric_trans/index.html')
    app_name = 'lyric_trans'
    context = {
        'form': form,
        'domain': domain,
        'app_name': app_name,
        'chat_results': trans_results
    }
    return HttpResponse(template.render(context, request))
