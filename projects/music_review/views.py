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
            model = form.cleaned_data['model']
            title = form.cleaned_data['title']
            artist = form.cleaned_data['artist']
            # print(artist)
            comment = form.cleaned_data['comment']
            source1 = form.cleaned_data['source1']
            source2 = form.cleaned_data['source2']
            wiki_discography = form.cleaned_data['wiki_discography']
            release_date = form.cleaned_data['release_date']
            label_manual = form.cleaned_data['label']
            producer_name = form.cleaned_data['producer_name']
            wiki_biography = form.cleaned_data['wiki_biography']
            spotyfi  = form.cleaned_data['spotyfi']
            youtube  = form.cleaned_data['youtube']
            recommend = form.cleaned_data['recommend']

            def get_body_text(url):
                if not url or not url.strip():
                    return ""
                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    return ""
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup.body.get_text()
                except requests.exceptions.RequestException as e:
                    return f"エラーが発生しました: {e}"

            def wiki_scrape_article(url: str) -> str:
                if not url or not url.strip():
                    return ""

                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    return ""

                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
                }

                resp = requests.get(url.strip(), headers=headers, timeout=20)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")  # lxml推奨
                # print("source", soup)
                # print("******** 1 ******************")

                # 脚注や編集リンクは削除
                for sel in ["sup.reference", "span.mw-editsection", "span.mw-cite-backlink"]:
                    for node in soup.select(sel):
                        node.decompose()

                # --- infobox ---
                infobox_table = soup.select_one(".infobox ")
                # print("infobox_table", infobox_table)
                # print("********* 2 ****************")
                if not infobox_table:
                    infobox_table = soup.select_one("table.infobox")

                infobox_text = ""
                if infobox_table:
                    infobox_text = infobox_table.get_text(separator="\n", strip=True)
                # print("infobox_text", infobox_text)
                # print("********* 3 ****************")
                # --- 本文 ---
                content_div = soup.select_one("div.mw-parser-output")
                # print("content_div", content_div)
                # print("********* 4 ****************")
                first_paragraphs_text = ""
                if content_div:
                    paragraphs = [
                        p.get_text(" ", strip=True)
                        for p in content_div.find_all("p", recursive=False)
                        if p.get_text(strip=True)
                    ]
                    first_paragraphs_text = "\n".join(paragraphs)

                combined_text = (infobox_text + "\n\n" + first_paragraphs_text).strip()
                # print("combined_text", combined_text)
                # print("********* 5 ****************")
                return combined_text


            # 共有のセッション（UA/言語を常に付ける）
            SESSION = requests.Session()
            SESSION.headers.update({
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
            })


            def wiki_get_data(url: str) -> dict:
                if not url or not url.strip():
                    return {}
                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    return {}

                # 取得（エラーコードは例外にする）
                resp = SESSION.get(url, timeout=20, allow_redirects=True)
                resp.raise_for_status()

                data = {}


                # パーサは lxml があれば使う / なければ標準にフォールバック
                parser = "lxml"
                try:
                    soup = BeautifulSoup(resp.text, parser)
                except Exception:
                    soup = BeautifulSoup(resp.text, "html.parser")

                # 余計な脚注や編集リンクは除去（見つからなくてもOK）
                for node in soup.select("sup.reference, span.mw-editsection, span.mw-cite-backlink"):
                    node.decompose()

                # --- 見出し（タイトル） ---
                heading_element = (
                    soup.find("h1", id="firstHeading")
                    or soup.select_one("#firstHeading")
                    or soup.select_one("h1.firstHeading")          # 念のためクラスでも
                    or soup.select_one("h1.mw-first-heading")      # モバイル/新スキン対策
                )

                if heading_element is None:
                    # ここに来るなら、記事ではなく別ページ（警告/同意/ブロック/429等）を掴んでいます
                    # デバッグ出力で中身を確認してください
                    print("DEBUG url:", resp.url, "status:", resp.status_code)
                    print("DEBUG <title>:", soup.title.string if soup.title else None)
                    print("DEBUG head snippet:", resp.text[:500])
                    return {}
                if heading_element:
                    data["title"] = heading_element.get_text(strip=True)
                print("DEBUG title_text:", data["title"])

                # artist
                artist_span = soup.find("span", itemprop="byArtist")
                if artist_span:
                    artist_link = artist_span.find("a")
                    if artist_link:
                        data["artist"] = artist_link.get_text(strip=True)

                # get genre
                # infobox 内の "Genre" 行を探す
                infobox = soup.select_one("table.infobox")
                genres_text = ""
                if infobox:
                    th = infobox.find("th", string=re.compile(r"^\s*Genre(s)?\s*$", re.I))
                    if th:
                        td = th.find_next("td")
                        if td:
                            # aタグを優先的に抽出
                            links = td.select("a[href]")
                            if links:
                                genres = [a.get_text(strip=True) for a in links]
                            else:
                                # aタグが無い場合はテキストをカンマ/スラッシュ区切りで分割
                                text = td.get_text(" ", strip=True)
                                genres = re.split(r"\s*(?:,|/|;)\s*", text)
                                genres = [g for g in genres if g]
                            genres_text = ", ".join(genres)
                data["genre"] = genres_text if genres_text else []

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
                if not url or not url.strip():
                    return []
                url = url.strip()
                if not url.startswith(('http://', 'https://')):
                    return []
                try:
                    response = requests.get(url)
                    response.encoding = response.apparent_encoding
                    soup = BeautifulSoup(response.text, "html.parser")
                    encore_text_elements = soup.find_all(class_='encore-text-body-medium')
                    return [element.get_text(strip=True) for element in encore_text_elements]
                except Exception:
                    return []

            source1_contents = ""
            if source1:
                source1_contents = get_body_text(source1)
            source2_contents = ""
            if source2:
                source2_contents = get_body_text(source2)
            wiki_discography_contents = wiki_scrape_article(wiki_discography)
            wiki_biography_contents = wiki_scrape_article(wiki_biography)
            wiki_discography_contents = wiki_scrape_article(wiki_discography)
            data = wiki_get_data(wiki_discography)
            tracklists = scrape_tracklist(spotyfi)
            formatted_list = '<br>\n'.join([f"{i+1}. {track}" for i, track in enumerate(tracklists)]) + '<br>'

            try:
                client = OpenAI(api_key=OPENAI_API_KEY)

                # --- レビュー生成 ---
                review_prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'review.txt')
                with open(review_prompt_path, 'r', encoding='utf-8') as f:
                    review_template = f.read()
                review_prompt_content = review_template.format(
                    comment=comment,
                    recommend=recommend,
                    wiki_biography_contents=wiki_biography_contents,
                    wiki_discography_contents=wiki_discography_contents,
                    source1_contents=source1_contents,
                    source2_contents=source2_contents,
                    artist_name=artist,
                    album_title=title,
                )
                review_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": review_prompt_content,
                        },
                    ],
                )
                review_result = review_response.choices[0].message.content

                # --- X投稿文生成 ---
                x_prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'x_post.txt')
                with open(x_prompt_path, 'r', encoding='utf-8') as f:
                    x_template = f.read()
                x_prompt_content = x_template.format(
                    review_result=review_result,
                    artist_name=artist,
                    album_title=title,
                )
                x_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": x_prompt_content,
                        },
                    ],
                )
                x_post_result = x_response.choices[0].message.content

                review = review_result.replace("\n", "<br>")
                x_post = x_post_result.replace("\n", "<br>")

                print(data.get('genre', ''))
                if data.get('genre'):
                    data['genre'] = ", ".join([f"#{genre.strip()}" for genre in data['genre'].split(",")])
                
                # 手動入力値を優先して使用
                final_label = label_manual if label_manual else data.get('label', '')
                if final_label:
                    final_label = ", ".join([f"#{genre.strip()}" for genre in final_label.split(",")])
                
                final_producer = producer_name if producer_name else data.get('producer', '')
                if final_producer:
                    final_producer = ", ".join([f"#{genre.strip()}" for genre in final_producer.split(",")])
                
                # 日付フォーマットを yyyy/mm/dd に統一
                final_release = ''
                if release_date:
                    final_release = release_date.strftime('%Y/%m/%d')
                elif data.get('release'):
                    final_release = data.get('release', '')
                format_title = ""
                format_artist = ""
                if title:
                    format_title = title.replace(" ", "")
                if artist:
                    format_artist = artist.replace(" ", "")

                chat_results = ""
                if title and artist:
                    chat_results += title + "／" + artist + "<br><br>"
                if source1:
                    chat_results += "<br><code>" + source1 + "</code><br>"
                if source2:
                    chat_results += "<br><code>" + source2 + "</code><br>"
                if spotyfi:
                    chat_results += "<br><code>" + spotyfi + "</code><br>"
                if youtube:
                    chat_results += "<br><code>" + youtube + "</code><br><br>"
                if format_title:
                    chat_results += "<br><br>TITLE: #" + format_title
                if format_artist:
                    chat_results += "<br>ARTIST: #" + format_artist
                if data.get('genre'):
                    chat_results += "<br>GENRE: " + data['genre']
                if final_producer:
                    chat_results += "<br>PRODUCER: " + final_producer
                if final_label:
                    chat_results += "<br>LABEL: " + final_label
                if final_release:
                    chat_results += "<br>RELEASE: " + final_release
                if review_result:
                    chat_results += "<br><br>REVIEW<br>" + review
                if recommend:
                    chat_results += "<br><br>RECOMMEND<br>" + recommend
                if formatted_list:
                    # chat_results += "<br><br>TRACKLISTS<br>" + renumbered_tracks
                    chat_results += "<br><br>TRACKLISTS<br>" + formatted_list
                if x_post_result:
                    chat_results += "<br><br>X POST<br>" + x_post
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



    return HttpResponse(template.render(context, request))
