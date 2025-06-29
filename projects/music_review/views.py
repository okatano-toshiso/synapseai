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
                if not url.strip():
                    return ""
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup.body.get_text()
                except requests.exceptions.RequestException as e:
                    return f"エラーが発生しました: {e}"

            def wiki_scrape_article(url):
                if not url.strip():
                    return ""
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
                if not url.strip():
                    return {}
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
                    
                    # Additional condition for producer
                    th_element = soup.find("th", class_="infobox-label")
                    if th_element and th_element.find("a") and th_element.find("a").get_text(strip=True) == "Producer":
                        td_element = th_element.find_next_sibling("td", class_="infobox-data hlist")
                        if td_element:
                            list_items = td_element.find_all("li")
                            producers = [item.get_text(strip=True) for item in list_items]
                            producer_text = ", ".join(producers)
                            print("producer_text", producer_text)
                data["producer"] = producer_text.replace(" ", "")

                return data

            def scrape_tracklist(url):
                if not url.strip():
                    return []
                try:
                    response = requests.get(url)
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.text, "html.parser")
                    encore_text_elements = soup.find_all(class_='encore-text-body-medium')
                    return [element.get_text(strip=True) for element in encore_text_elements]
                except Exception:
                    return []

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
                            あなたは一流の音楽評論家です。以下の情報をもとに、日本語で構成された音楽レビュー記事を執筆してください。

                            【ユーザーコメント】
                            {comment}
                            （お気に入りの曲：{recommend}）

                            【アーティスト情報（Wikipedia）】
                            {wiki_biography_contents}

                            【ディスコグラフィ（Wikipedia）】
                            {wiki_discography_contents}

                            【アーティスト情報（公式サイト）】
                            {official_biography}

                            【ディスコグラフィ（公式サイト）】
                            {official_discography}

                            ---

                            ◉ 執筆構成：

                            記事は以下の3セクションで構成してください：

                            ◆アーティストの紹介（200〜300文字程度）  
                            - アーティストの出自、経歴、音楽スタイル、過去の代表作など  
                            - Wikipedia・公式情報に基づき客観的かつ簡潔にまとめる  

                            ◆アルバムの評論（700〜800文字程度）  
                            - 【起】本作の立ち位置（転機、復帰作など）と全体印象  
                            - 【承】サウンド、ジャンル、構成、プロダクション分析  
                            - 【転】印象的な楽曲の解釈や歌詞の掘り下げ  
                            - 【結】総評としての意義、リスナーへのメッセージ  


                            ---

                            ◉ 制約：
                            - 「アーティストの紹介」というタイトルを入れてください 
                            - 「アルバムの評論」というタイトルを入れてください 
                            - 出力は**1000文字以内**に収めてください  
                            - **日本語**で、評論文として自然で洗練された文体を使用してください  
                            - ユーザーのコメントや推し曲情報も参考にしてください  
                            """

                        },
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
                if youtube:
                    chat_results += "<br>YOUTUBE: " + youtube
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



