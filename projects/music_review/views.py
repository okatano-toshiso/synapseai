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
            title = form.cleaned_data['title']
            artist = form.cleaned_data['artist']
            # print(artist)
            comment = form.cleaned_data['comment']
            official_site_discography = form.cleaned_data['official_site_discography']
            official_site_biography = form.cleaned_data['official_site_biography']
            wiki_discography = form.cleaned_data['wiki_discography']
            wiki_biography = form.cleaned_data['wiki_biography']
            spotyfi  = form.cleaned_data['spotyfi']
            youtube  = form.cleaned_data['youtube']
            recommend = form.cleaned_data['recommend']

            def get_body_text(url):
                try:
                    response = requests.get(url)
                    response.raise_for_status()  # HTTPエラーが発生した場合に例外を発生させる
                    soup = BeautifulSoup(response.content, 'html.parser')
                    body_text = soup.body.get_text()
                    return body_text

                except requests.exceptions.RequestException as e:
                    return f"エラーが発生しました: {e}"

            def wiki_scrape_article(url):
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "html.parser")
                infobox_table = soup.find("table", class_="infobox")
                if infobox_table:
                    infobox_text = infobox_table.get_text(separator="\n", strip=True)
                first_paragraphs_text = ""
                content_div = soup.find("div", class_="mw-content-ltr mw-parser-output")
                if content_div:
                    paragraphs = content_div.find_all("p")
                    if paragraphs:
                        first_paragraphs_text = "\n".join(p.get_text(strip=True) for p in paragraphs)
                    else:
                        first_paragraphs_text = ""
                combined_text = infobox_text + "\n\n" + first_paragraphs_text
                return combined_text

            def wiki_get_data(url):
                data = {}  
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "html.parser")

                # title
                heading_element = soup.find("h1", class_="firstHeading")
                if heading_element:
                    data["title"] = heading_element.get_text(strip=True)

                # artist
                artist_span = soup.find("span", itemprop="byArtist")
                if artist_span:
                    artist_link = artist_span.find("a")
                    if artist_link:
                        data["artist"] = artist_link.get_text(strip=True)

                # get genre
                genre_element = soup.find(attrs={"itemprop": "genre"})
                genres_text = ""
                if genre_element:
                    plainlist_div = genre_element.find(class_="plainlist")
                    if plainlist_div:
                        list_items = plainlist_div.find_all("li")
                        genres = [item.get_text(strip=True) for item in list_items]
                        genres_text = ", ".join(genres)
                        data["genre"] = genres_text
                    else:
                        # If no plainlist class is found, get the text from all <a> tags
                        genres  = [a.get_text(strip=True) for a in genre_element.find_all("a")]
                        genres_text = ", ".join(genres)
                        data["genre"] = genres_text
                else:
                    # If genre_element is not found, set genre to an empty list
                    data["genre"] = []

                # release
                date_published_element = soup.find("time", itemprop="datePublished")
                if not date_published_element:
                    date_published_element = soup.find("td", class_="infobox-data")
                print(date_published_element)
                if date_published_element:
                    plainlist_div = date_published_element.find("div", class_="plainlist")
                    if plainlist_div:
                        first_li = plainlist_div.find("li")  # 最初の <li> 要素を取得
                        if first_li:
                            data["release"] = first_li.get_text(strip=True)
                    else:
                        data["release"] = date_published_element.get_text(strip=True)

                # label
                publisher_element = soup.find(attrs={"itemprop": "publisher"})
                publisher_text = ""
                if publisher_element:
                    plainlist_divs = publisher_element.find_all("div", class_="plainlist")  # find_all を使った場合
                    publishers = []
                    for plainlist_div in plainlist_divs:  # 各 plainlist_div をループ処理
                        list_items = plainlist_div.find_all("li")
                        publishers.extend([item.get_text(strip=True) for item in list_items])
                    if not publishers:  # If no plainlist items are found, check for itemprop="name"
                        name_elements = publisher_element.find_all(attrs={"itemprop": "name"})
                        publishers = [name.get_text(strip=True) for name in name_elements]
                    publisher_text = ", ".join(publishers)
                else:
                    # plainlist_divs = publisher_element.find_all("div", class_="plainlist")
                    if publisher_element:
                        data["label"] = publisher_element.get_text(strip=True)
                    else:
                        publisher_text = ""

                # 新しい条件を追加
                if not publisher_text:
                    hlist_element = soup.find("td", class_="infobox-data hlist")
                    if hlist_element:
                        a_elements = hlist_element.find_all("a")
                        publisher_text = ", ".join([a.get_text(strip=True) for a in a_elements])
                    print(publisher_text)
                    if hlist_element:
                        publisher_text = hlist_element.get_text(strip=True)

                data["label"] = publisher_text.replace(" ", "")

                # producer
                producer_element = soup.find(attrs={"itemprop": "producer"})
                producer_text = ""
                if producer_element:
                    plainlist_div = producer_element.find("div", class_="plainlist")
                    if plainlist_div:
                        list_items = plainlist_div.find_all("li")
                        producers = [item.get_text(strip=True) for item in list_items]
                        producer_text = ", ".join(producers)
                    else:
                        # If no plainlist class is found, get all itemprop="name" elements and combine their text
                        name_elements = producer_element.find_all(attrs={"itemprop": "name"})
                        producers = [name.get_text(strip=True) for name in name_elements]
                        producer_text = ", ".join(producers)
                else:
                    # New condition for producer
                    hlist_div = soup.find("div", class_="hlist")
                    if hlist_div:
                        list_items = hlist_div.find_all("li")
                        producers = [item.get_text(strip=True) for item in list_items]
                        producer_text = ", ".join(producers)
                data["producer"] = producer_text.replace(" ", "")

                return data

            def scrape_tracklist(url):
                response = requests.get(url)
                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, "html.parser")
                encore_text_elements = soup.find_all(class_='encore-text-body-medium')
                encore_text_list = [element.get_text(strip=True) for element in encore_text_elements]
                return encore_text_list

            official_discography = ""
            if official_site_discography != "":
                official_discography = get_body_text(official_site_discography)
            official_biography = ""
            if official_site_biography != "":
                official_biography = get_body_text(official_site_biography)
            wiki_discography_contents = wiki_scrape_article(wiki_discography)
            wiki_biography_contents = wiki_scrape_article(wiki_biography)
            wiki_discography_contents = wiki_scrape_article(wiki_discography)
            data = wiki_get_data(wiki_discography)
            tracklists = scrape_tracklist(spotyfi)
            formatted_list = '<br>\n'.join([f"{i+1}. {track}" for i, track in enumerate(tracklists)]) + '<br>'

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
                            システムは優秀な音楽評論家です。下記の情報をもとに作品のレビューを書いてください。
                            ユーザーのコメント
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {comment}
                            お気に入りの曲は{recommend}です。
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            アーティストの情報
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {wiki_biography_contents}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            作品の情報
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {wiki_discography_contents}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            公式サイトの作品テキスト
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {official_discography}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            公式サイトのアーティスト情報
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {official_biography}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n

                            アルバムの説明、アルバムの制作背景、収録曲、世評、社会に与えた影響などがあればレビューしてください。
                            この音楽作品の評論を書いています。400文字以内に綺麗に校正してまとめてください。
                            必ず日本語で回答してください。
                            """
                        }
                    ],
                )
                review_result = review.choices[0].message.content
                review = review_result.replace("\n", "<br>")

                print(data.get('genre', ''))
                if data.get('genre'):
                    data['genre'] = ", ".join([f"#{genre.strip()}" for genre in data['genre'].split(",")])
                if data.get('label'):
                    data['label'] = ", ".join([f"#{genre.strip()}" for genre in data['label'].split(",")])
                if data.get('producer'):
                    data['producer'] = ", ".join([f"#{genre.strip()}" for genre in data['producer'].split(",")])
                format_title = ""
                format_artist = ""
                if title:
                    format_title = title.replace(" ", "")
                if artist:
                    format_artist = artist.replace(" ", "")

                chat_results = ""
                if title and artist:
                    chat_results += title + "／" + artist + "<br><br>"
                if official_site_discography:
                    chat_results += official_site_discography + "<br>"
                if spotyfi:
                    chat_results += spotyfi
                if format_title:
                    chat_results += "<br><br>TITLE: #" + format_title
                if format_artist:
                    chat_results += "<br>ARTIST: #" + format_artist
                if data.get('genre'):
                    chat_results += "<br>GENRE: " + data['genre']
                if data.get('producer'):
                    chat_results += "<br>PRODUCER: " + data['producer']
                if data.get('label'):
                    chat_results += "<br>LABEL: " + data['label']
                if data.get('release'):
                    chat_results += "<br>RELEASE: " + data['release']
                if youtube:
                    chat_results += "<br>YOUTUBE: " + youtube
                if review_result:
                    chat_results += "<br><br>REVIEW<br>" + review
                if recommend:
                    chat_results += "<br><br>RECOMMEND<br>" + recommend
                if formatted_list:
                    # chat_results += "<br><br>TRACKLISTS<br>" + renumbered_tracks
                    chat_results += "<br><br>TRACKLISTS<br>" + formatted_list
                # if members:
                #     chat_results += "<br><br>PERSONAL<br>" + formatted_member_list


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
        'app_name': 'music_review',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))



