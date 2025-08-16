from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI
import re
from bs4 import BeautifulSoup
import requests

def clean_and_format_members(member_list):
    members = member_list.split("\n")
    cleaned_members = []
    for member in members:
        cleaned_member = re.sub(r'\s*–.*$', '', member)
        cleaned_member = cleaned_member.replace(" ", "")
        cleaned_member = re.sub(r'：.*$', '', cleaned_member)
        cleaned_member = f"#{cleaned_member}"
        cleaned_members.append(cleaned_member)
    return "\n".join(cleaned_members)

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title'].replace(" ", "")
            if not form.cleaned_data['artist'].replace(" ", "").startswith('#'):
                artist = "#" + re.sub(r',\s*', ' #', form.cleaned_data['artist'].replace(" ", ""))
            if not form.cleaned_data['genre'].replace(" ", "").startswith('#'):
                genre = "#" + re.sub(r',\s*', ' #', form.cleaned_data['genre'].replace(" ", ""))
            if not form.cleaned_data['producer'].replace(" ", "").startswith('#'):
                producer = "#" + re.sub(r',\s*', ' #', form.cleaned_data['producer'].replace(" ", ""))
            spotyfi  = form.cleaned_data['spotyfi']
            youtube  = form.cleaned_data['youtube']
            if not form.cleaned_data['label'].replace(" ", "").startswith('#'):
                label = "#" + re.sub(r',\s*', ' #', form.cleaned_data['label'].replace(" ", ""))
            recommend = form.cleaned_data['recommend']
            track_list = form.cleaned_data['track_list']
            members = form.cleaned_data['members']
            if 'release' in form.cleaned_data and form.cleaned_data['release'] is not None:
                release = form.cleaned_data['release']
                release = release.strftime('%Y-%m-%d')
            else:
                release = ''
            review = form.cleaned_data['review']
            biography = form.cleaned_data['biography']



            def biography_scrape_article(url):
                joined_text = ""
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "html.parser")
                content_div = soup.find("div", id="mw-content-text", class_="mw-body-content")
                if content_div:
                    joined_text += content_div.get_text(separator="\n")  # テキストを改行で区切って取得
                return joined_text
            url = "https://en.wikipedia.org/wiki/The_Beach_Boys"
            biography = biography_scrape_article(url)
            print(biography)




            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                review = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            システムは優秀な音楽評論家です。下記の情報をもとにレビューを書いてください。
                            必ず日本語で回答してください。
                            必要であれば、{artist}の作品「{title}」についてネットで調べてください。
                            {artist}のバイオグラフィーは下記になります。
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {biography}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {title}の情報は下記になります。
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {review}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            アルバムの説明、アルバムの制作背景、収録曲、世評、社会に与えた影響などがあればレビューしてください。
                            この音楽作品の評論を書いています。600文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                review_result = review.choices[0].message.content
                review_result = review_result.replace("\n", "<br>")

                # tracklist = track_list.split("\n")
                # cleaned_tracks = []
                # for track in tracklist:
                #     cleaned_track = re.sub(r'^\d+\.\s*', '', track)
                #     if '"' in cleaned_track:
                #         cleaned_track = re.sub(r'"[^"]*"$', '', cleaned_track)
                #         match = re.search(r'"([^"]*)"', cleaned_track)
                #         if match:
                #             cleaned_track = match.group(1)
                #     cleaned_tracks.append(cleaned_track)
                # renumbered_tracks = []
                # for i, track in enumerate(cleaned_tracks, start=1):
                #     renumbered_tracks.append(f"{i}. {track}")

                tracklist = track_list.split("\n")
                cleaned_tracks = []
                renumbered_tracks = []
                track_number = 1

                for track in tracklist:
                    # DISCの検出（そのまま追加し、次のトラックから再ナンバリング）
                    if re.match(r'Disc\s*\d+', track):
                        renumbered_tracks.append("\n")
                        renumbered_tracks.append(track)
                        track_number = 1  # DISCの次は1から採番
                        continue
                    # トラック番号の除去
                    cleaned_track = re.sub(r'^\d+\.\s*', '', track)
                    # 引用符または「」で囲まれたテキストの処理
                    if '"' in cleaned_track or '「' in cleaned_track:
                        # 引用符で囲まれたテキストを削除
                        cleaned_track = re.sub(r'"[^"]*"$', '', cleaned_track)
                        # cleaned_track = re.sub(r'「[^」]*」.*$', '', cleaned_track)  # 「」内とその後の文字を削除
                        # 「」または""内のテキストを抽出して代入
                        match = re.search(r'"([^"]*)"', cleaned_track) or re.search(r'「([^」]*)」', cleaned_track)
                        if match:
                            cleaned_track = match.group(1)
                    # 再ナンバリングしてリストに追加
                    renumbered_tracks.append(f"{track_number}. {cleaned_track}")
                    track_number += 1

                formatted_member_list = clean_and_format_members(members)
                formatted_member_list = formatted_member_list.replace("\n", "<br>")

                chat_results = ""
                if spotyfi:
                    chat_results += spotyfi
                if title:
                    chat_results += "<br><br>TITLE: #" + title
                if artist:
                    chat_results += "<br>ARTIST: " + artist
                if genre:
                    chat_results += "<br>GENRE: " + genre
                if producer:
                    chat_results += "<br>PRODUCER: " + producer
                if label:
                    chat_results += "<br>LABEL: " + label
                if release:
                    chat_results += "<br>RELEASE: " + release
                if youtube:
                    chat_results += "<br>YOUTUBE: " + youtube
                if review_result:
                    chat_results += "<br><br>REVIEW<br>" + review_result
                if recommend:
                    chat_results += "<br><br>RECOMMEND<br>" + recommend
                if renumbered_tracks:
                    # chat_results += "<br><br>TRACKLISTS<br>" + renumbered_tracks
                    chat_results += "<br><br>TRACKLISTS<br>" + "<br>".join(renumbered_tracks)
                if members:
                    chat_results += "<br><br>PERSONAL<br>" + formatted_member_list
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('diary/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'diary',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))



