from django.http import HttpResponse
from django.template import loader
from .forms import TtsForm
import os
from openai import OpenAI
from django.core.files import File  # ファイル操作のためにインポート
from django.conf import settings  # 設定値を取得するためにインポート

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = TtsForm(request.POST)
        if form.is_valid():
            sentence = form.cleaned_data['sentence']
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                speech_file_path = settings.BASE_DIR / "uploads/tts/speech.mp3"
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=sentence
                )
                response.stream_to_file(speech_file_path)
                chat_results = speech_file_path
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = TtsForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('tts/index.html')
    auto_play = True
    context = {
        'form': form,
        'domain': domain,
        'chat_results': chat_results,
        'auto_play': auto_play
    }
    return HttpResponse(template.render(context, request))

def delete_file(request):
    file_path = settings.BASE_DIR / "uploads/tts/speech.mp3"
    if os.path.exists(file_path):
        os.remove(file_path)
        return HttpResponse("File deleted successfully", status=200)
    else:
        return HttpResponse("File not found", status=404)
