from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            artist = form.cleaned_data['artist']
            genre = form.cleaned_data['genre']
            producer  = form.cleaned_data['producer']
            label = form.cleaned_data['label']
            recommend = form.cleaned_data['recommend']
            track_list = form.cleaned_data['track_list']
            members = form.cleaned_data['members']
            if 'release' in form.cleaned_data and form.cleaned_data['release'] is not None:
                release = form.cleaned_data['release']
                release = release.strftime('%Y-%m-%d')
            else:
                release = ''
            review = form.cleaned_data['review']
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                review = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            導入部
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {review}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            この音楽作品の評論を書いています。300文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                review_result = review.choices[0].message.content
                review_result = review_result.replace("\n", "<br>")
                print(review_result)

                tracks = track_list.split("\n")
                numbered_track_list = ""
                for i, track in enumerate(tracks, start=1):
                    numbered_track_list += f"{i}. {track}<br>"
                members = members.replace("\n", "<br>")
                chat_results = "アルバム名:" + title + "<br>アーティスト:" + artist + "<br>ジャンル:" + genre + "<br>プロデューサー:" + producer + "<br>レーベル:" + label + "<br>リリース:" + release + "<br><br>レビュー：<br>" + review_result + "<br><br>おすすめ曲：<br>" + recommend + "<br><br>収録曲：<br>" + numbered_track_list + "<br><br>参加メンバー：<br>" + members

            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('music_review/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
