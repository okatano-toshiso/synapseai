from django.http import HttpResponse
from django.template import loader
from .forms import TranscribeForm
import os
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files import File  # ファイル操作のためにインポート
from django.conf import settings  # 設定値を取得するためにインポート
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

@csrf_exempt
def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = TranscribeForm(request.POST)
        if form.is_valid():
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                audio_file_path = settings.BASE_DIR / "uploads/english/user.wav"
                audio_file= open(audio_file_path , "rb")
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": """
                                New users come to Tsunaga
                                The system is an excellent teacher of English
                                You teach English to users who are your students
                                You must speak english

                                You speak English all the time and nothing but English
                                You have a variety of problems for your students
                                You have a lot of everyday conversation

                                My favorite drink is coffee and my favorite food is ramen.
                                I love Japan.

                                He likes baseball and will talk about baseball.
                            """
                        },
                        {
                            "role": "user",
                            "content": transcription.text
                        },
                    ],
                )
                text_results = response.choices[0].message.content
                speech_file_path = settings.BASE_DIR / "uploads/english/system.mp3"
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy",
                    input=text_results
                )
                response.stream_to_file(speech_file_path)
                chat_results = speech_file_path
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = TranscribeForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('english/index.html')
    auto_play = True
    app_name = "english"
    context = {
        'domain': domain,
        'chat_results': chat_results,
        'app_name': app_name,
        'auto_play': auto_play
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_POST
def upload_audio(request):
    audio_file = request.FILES.get('audioFile')
    if not audio_file:
        return JsonResponse({'error': '音声ファイルが提供されていません。'}, status=400)
    save_path = os.path.join(settings.MEDIA_ROOT, 'english', audio_file.name)
    # ファイルの保存
    with open(save_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    return JsonResponse({'message': 'ファイルが正常にアップロードされました。'})
def delete_file(request):
    # 削除したいファイルのパス
    files = [
        settings.BASE_DIR / "uploads/english/system.mp3",
        settings.BASE_DIR / "uploads/english/user.wav"
    ]
    responses = []
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            return HttpResponse("File deleted successfully", status=200)
        else:
            return HttpResponse("File not found", status=404)

