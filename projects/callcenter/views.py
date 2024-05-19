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
                audio_file_path = settings.BASE_DIR / "uploads/callcenter/user.wav"
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
                            新しいひとがやってきます
                            日本語で応答してください
                            あなたは浄水器のコールセンターで働くコールガールです。
                            この役割では、コールセンターで働く女性スタッフが、浄水器に関するお客様からの問い合わせに対応します。
                            彼女は親切で丁寧な対応を心がけ、浄水器の特徴やメリット、使い方、保守に関する質問に答えることが求められます。
                            例えば、浄水器の取り付け方法、フィルターの交換時期や方法、浄水性能についての説明が必要です。
                            また、購入後のアフターサポートに関する情報も提供します。彼女の役割は、顧客がこの浄水器を安心して使用できるように、正確かつ有用な情報を提供することです。
                            商品についての情報を記載します。
                            ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
                            この浄水器は、家庭用に設計されており、価格は4800円です。
                            寿命は1年間有効で、交換用のフィルターが必要になります。
                            デザインはコンパクトでモダンなものを想定し、主にキッチンカウンターに置くことを考慮したスタイルです。
                            この浄水器は、蛇口に直接取り付けるタイプであり、取り付けはユーザー自身で簡単にできるように設計されています。
                            浄水機能としては、塩素、重金属、細菌を効率的に除去し、水道水を安全で美味しい飲料水に変換します。
                            また、エコフレンドリーな素材を使用し、環境に優しい製品となっています。
                            ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー
                            商品の問い合わせ対応のみ回答してください。
                            """
                        },
                        {
                            "role": "user",
                            "content": transcription.text
                        },
                    ],
                )
                text_results = response.choices[0].message.content
                speech_file_path = settings.BASE_DIR / "uploads/callcenter/system.mp3"
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
    template = loader.get_template('callcenter/index.html')
    auto_play = True
    app_name = "callcenter"
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
    save_path = os.path.join(settings.MEDIA_ROOT, 'callcenter', audio_file.name)
    # ファイルの保存
    with open(save_path, 'wb+') as destination:
        for chunk in audio_file.chunks():
            destination.write(chunk)
    return JsonResponse({'message': 'ファイルが正常にアップロードされました。'})
def delete_file(request):
    # 削除したいファイルのパス
    files = [
        settings.BASE_DIR / "uploads/callcenter/system.mp3",
        settings.BASE_DIR / "uploads/callcenter/user.wav"
    ]
    responses = []
    for file_path in files:
        if os.path.exists(file_path):
            os.remove(file_path)
            return HttpResponse("File deleted successfully", status=200)
        else:
            return HttpResponse("File not found", status=404)

