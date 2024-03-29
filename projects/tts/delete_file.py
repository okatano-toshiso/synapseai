from django.http import HttpResponse
import os

def delete_file(request):
    # 削除したいファイルのパス
    file_path = settings.BASE_DIR / "uploads/tts/speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)
        return HttpResponse("File deleted successfully", status=200)
    else:
        return HttpResponse("File not found", status=404)
