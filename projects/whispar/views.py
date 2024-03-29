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
    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    chat_results = ""
    if request.method == "POST":
        form = TranscribeForm(request.POST)
        if form.is_valid():
            client = OpenAI(
                api_key = OPENAI_API_KEY,
            )
            audio_file_path = settings.BASE_DIR / "uploads/uploads/recording.wav"
            print(audio_file_path)
            audio_file= open(audio_file_path , "rb")
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            chat_results = transcription.text
            # if default_storage.exists(audio_file_path):
            #     default_storage.delete(audio_file_path)
    else:
        form = TranscribeForm()
    domain = request.build_absolute_uri('/')
    template = loader.get_template('whispar/index.html')
    context = {
        'domain': domain,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))

@csrf_exempt
@require_POST
def upload_audio(request):
    audio_file = request.FILES.get('audioFile')
    if not audio_file:
        return JsonResponse({'error': '音声ファイルが提供されていません。'}, status=400)

    # ファイル保存パスの生成
    # settings.MEDIA_ROOTは、settings.pyで定義されているメディアファイルのルートディレクトリ
    # 'uploads'は、その中の任意のサブディレクトリ（存在しない場合は作成する必要がある）
    save_path = os.path.join(settings.MEDIA_ROOT, 'uploads', audio_file.name)

    # ファイルの保存
    with open(save_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)

    return JsonResponse({'message': 'ファイルが正常にアップロードされました。'})

def delete_file(request):
    # 削除したいファイルのパス
    file_path = settings.BASE_DIR / "uploads/uploads/recording.wav"

    if os.path.exists(file_path):
        os.remove(file_path)
        return HttpResponse("File deleted successfully", status=200)
    else:
        return HttpResponse("File not found", status=404)