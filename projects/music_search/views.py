from django.http import HttpResponse
from django.template import loader
from .forms import MusicSearchForm
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote, urljoin


def index(request):
    search_results = {}
    
    if request.method == "POST":
        form = MusicSearchForm(request.POST)
        if form.is_valid():
            language = form.cleaned_data['language']
            artist_name = form.cleaned_data['artist_name']
            album_name = form.cleaned_data.get('album_name', '').strip()
            
            # Wikipedia検索
            wiki_base_url = "https://ja.wikipedia.org" if language == "ja" else "https://en.wikipedia.org"
            artist_wiki_url = search_wikipedia_artist(artist_name, wiki_base_url)
            
            # アルバムのWikipedia URL検索（任意）
            album_wiki_url = ''
            if album_name:
                album_wiki_url = search_wikipedia_album(artist_name, album_name, wiki_base_url)
            
            # アルバム一覧の取得（従来の全取得ロジック）
            albums = get_artist_albums_from_wikipedia(artist_wiki_url, wiki_base_url)
            
            # 公式サイト情報の取得
            official_urls = get_official_urls_from_wikipedia(artist_wiki_url)
            
            search_results = {
                'artist_name': artist_name,
                'album_name': album_name,
                'album_wiki_url': album_wiki_url,
                'language': '邦楽' if language == 'ja' else '洋楽',
                'artist_wiki_url': artist_wiki_url,
                'official_biography_url': official_urls.get('biography', ''),
                'official_discography_url': official_urls.get('discography', ''),
                'albums': albums
            }
    else:
        form = MusicSearchForm()
    
    template = loader.get_template('music_search/index.html')
    domain = request.build_absolute_uri('/')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'music_search',
        'search_results': search_results
    }
    return HttpResponse(template.render(context, request))


def search_wikipedia_artist(artist_name, base_url):
    """Wikipediaでアーティストを検索してURLを返す（存在確認済み）"""
    search_url = f"{base_url}/wiki/{quote(artist_name.replace(' ', '_'))}"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 直接URLを試す
        response = requests.get(search_url, headers=headers, timeout=10, allow_redirects=True)
        
        # 200かつ検索ページや存在しないページでないことを確認
        if response.status_code == 200 and '/w/index.php' not in response.url:
            soup = BeautifulSoup(response.content, 'html.parser')
            # "Wikipedia does not have an article"などのエラーページでないか確認
            noarticletext = soup.select_one('.noarticletext')
            if not noarticletext:
                return response.url
        
        # MediaWiki Search APIで検索
        api_url = f"{base_url}/w/api.php"
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': artist_name,
            'srlimit': 5,
            'format': 'json'
        }
        api_response = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = api_response.json()
        results = data.get('query', {}).get('search', [])
        
        # 検索結果から最適なページを選択
        if results:
            for result in results:
                title = result.get('title', '')
                # アーティスト名が含まれるタイトルを優先
                if artist_name.lower() in title.lower():
                    candidate_url = f"{base_url}/wiki/{quote(title.replace(' ', '_'))}"
                    # URLが実際に存在するか確認
                    check_response = requests.get(candidate_url, headers=headers, timeout=10, allow_redirects=True)
                    if check_response.status_code == 200 and '/w/index.php' not in check_response.url:
                        soup = BeautifulSoup(check_response.content, 'html.parser')
                        noarticletext = soup.select_one('.noarticletext')
                        if not noarticletext:
                            return check_response.url
            
            # 完全一致がない場合は最初の結果を試す
            first_title = results[0].get('title', '')
            candidate_url = f"{base_url}/wiki/{quote(first_title.replace(' ', '_'))}"
            check_response = requests.get(candidate_url, headers=headers, timeout=10, allow_redirects=True)
            if check_response.status_code == 200 and '/w/index.php' not in check_response.url:
                soup = BeautifulSoup(check_response.content, 'html.parser')
                noarticletext = soup.select_one('.noarticletext')
                if not noarticletext:
                    return check_response.url
                    
    except Exception as e:
        print(f"Wikipedia検索エラー: {e}")
    
    return ""


def search_wikipedia_album(artist_name, album_name, base_url):
    """アーティスト名とアルバム名からWikipediaのアルバムURLを返す
    「アーティスト名 タイトル名 WIKI」で検索した結果を使用し、存在確認を実施"""
    if not album_name:
        return ""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # 1) 有力な候補タイトルを直接叩いて確認（存在確認を強化）
        title_basic = album_name.strip()
        candidates = [
            f"{base_url}/wiki/{quote(title_basic.replace(' ', '_'))}",
            f"{base_url}/wiki/{quote((title_basic + ' (album)').replace(' ', '_'))}",
            f"{base_url}/wiki/{quote((title_basic + '_(album)').replace(' ', '_'))}",
            f"{base_url}/wiki/{quote((title_basic + ' (アルバム)').replace(' ', '_'))}",
            f"{base_url}/wiki/{quote((title_basic + '_(アルバム)').replace(' ', '_'))}",
        ]
        
        for url in candidates:
            try:
                r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                # 200かつ検索ページや存在しないページでないことを確認
                if r.status_code == 200 and '/w/index.php' not in r.url:
                    soup = BeautifulSoup(r.content, 'html.parser')
                    # "Wikipedia does not have an article"などのエラーページでないか確認
                    noarticletext = soup.select_one('.noarticletext')
                    if not noarticletext:
                        # アーティスト名が本文に含まれているか確認（関連性チェック）
                        content = soup.select_one('#mw-content-text')
                        if content and artist_name.lower() in content.get_text().lower():
                            print(f"候補URL確認成功: {r.url}")
                            return r.url
            except Exception as e:
                print(f"候補URL確認エラー: {e}")
        
        # 2) MediaWiki Search APIで「アーティスト名 アルバム名」で検索
        api_url = f"{base_url}/w/api.php"
        # 「アーティスト名 タイトル名」で検索（WIKIキーワードは暗黙的）
        search_query = f'{artist_name} {album_name}'
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': search_query,
            'srlimit': 10,
            'format': 'json'
        }
        resp = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = resp.json()
        results = data.get('query', {}).get('search', [])
        
        if results:
            lower_album = album_name.lower()
            lower_artist = artist_name.lower()
            
            # 検索結果から最適なページを選択
            for item in results:
                title = item.get('title', '')
                t_low = title.lower()
                
                # アルバム名とアーティスト名の両方を含むタイトルを優先
                if lower_album in t_low and (lower_artist in t_low or 'album' in t_low or 'アルバム' in t_low):
                    candidate_url = urljoin(base_url, '/wiki/' + quote(title.replace(' ', '_')))
                    
                    # URLが実際に存在するか確認
                    try:
                        check_response = requests.get(candidate_url, headers=headers, timeout=10, allow_redirects=True)
                        if check_response.status_code == 200 and '/w/index.php' not in check_response.url:
                            soup = BeautifulSoup(check_response.content, 'html.parser')
                            noarticletext = soup.select_one('.noarticletext')
                            if not noarticletext:
                                # アーティスト名が本文に含まれているか確認
                                content = soup.select_one('#mw-content-text')
                                if content and lower_artist in content.get_text().lower():
                                    print(f"検索結果から確認成功: {check_response.url}")
                                    return check_response.url
                    except Exception as e:
                        print(f"検索結果の確認エラー: {e}")
                        continue
            
            # 完全一致がない場合でも、アルバム名を含む最初の結果を試す
            for item in results:
                title = item.get('title', '')
                if lower_album in title.lower():
                    candidate_url = urljoin(base_url, '/wiki/' + quote(title.replace(' ', '_')))
                    try:
                        check_response = requests.get(candidate_url, headers=headers, timeout=10, allow_redirects=True)
                        if check_response.status_code == 200 and '/w/index.php' not in check_response.url:
                            soup = BeautifulSoup(check_response.content, 'html.parser')
                            noarticletext = soup.select_one('.noarticletext')
                            if not noarticletext:
                                print(f"フォールバック確認成功: {check_response.url}")
                                return check_response.url
                    except Exception:
                        continue
                        
    except Exception as e:
        print(f"アルバム検索エラー: {e}")
    
    # 存在しないページは返さない
    print(f"アルバム「{album_name}」のWikipediaページが見つかりませんでした")
    return ""

def get_official_urls_from_wikipedia(wiki_url):
    """WikipediaページからアーティストのデフォルトURLを取得"""
    urls = {'biography': '', 'discography': ''}
    
    if not wiki_url:
        return urls
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(wiki_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Infoboxから公式サイトURLを探す
        infobox = soup.select_one('table.infobox')
        if infobox:
            # 公式サイトのリンクを探す
            for row in infobox.find_all('tr'):
                th = row.find('th')
                if th and ('website' in th.get_text().lower() or '公式' in th.get_text()):
                    td = row.find('td')
                    if td:
                        link = td.find('a', href=True)
                        if link:
                            official_site = link['href']
                            # バイオグラフィとディスコグラフィのURLを推測
                            urls['biography'] = f"{official_site}/biography" if not official_site.endswith('/') else f"{official_site}biography"
                            urls['discography'] = f"{official_site}/discography" if not official_site.endswith('/') else f"{official_site}discography"
                            break
    except Exception as e:
        print(f"公式URL取得エラー: {e}")
    
    return urls


def get_artist_albums_from_wikipedia(wiki_url, base_url):
    """WikipediaページからアーティストのStudio albumsを取得"""
    albums = []
    
    if not wiki_url:
        return albums
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # まずDiscographyセクションへのリンクを探す
        discography_url = None
        response = requests.get(wiki_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Discographyセクションを探して、別ページへのリンクがあるか確認
        content = soup.select_one('div.mw-parser-output')
        if content:
            for heading in content.find_all(['h2', 'h3']):
                heading_text = heading.get_text().lower()
                if 'discography' in heading_text or 'ディスコグラフィ' in heading_text:
                    # "Main article:"へのリンクを探す
                    current = heading.find_next_sibling()
                    while current and current.name not in ['h2']:
                        if current.name == 'div' and 'hatnote' in current.get('class', []):
                            link = current.find('a', href=True)
                            if link and '/wiki/' in link['href']:
                                discography_url = urljoin(base_url, link['href'])
                                break
                        current = current.find_next_sibling()
                    break
        
        # Discography専用ページがあればそちらを使用
        if discography_url:
            print(f"Discographyページを使用: {discography_url}")
            response = requests.get(discography_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.select_one('div.mw-parser-output')
        
        # Studio albumsセクションを探す（複数のパターンに対応）
        if content:
            studio_albums_found = False
            
            # パターン1: h2/h3/h4見出しとしてのStudio albums
            for heading in content.find_all(['h2', 'h3', 'h4']):
                heading_text = heading.get_text().lower()
                
                if 'studio album' in heading_text or 'スタジオ・アルバム' in heading_text or 'スタジオアルバム' in heading_text:
                    print(f"Studio albumsセクション（見出し）を発見: {heading.get_text()}")
                    studio_albums_found = True
                    
                    # テーブル形式を探す
                    current = heading.find_next_sibling()
                    while current and current.name not in ['h2', 'h3', 'h4']:
                        if current.name == 'table' and 'wikitable' in current.get('class', []):
                            print("テーブルを発見、アルバム情報を抽出中...")
                            for row in current.find_all('tr')[1:]:
                                cells = row.find_all(['td', 'th'])
                                if cells and len(cells) > 0:
                                    album_link = cells[0].find('a', href=True)
                                    if album_link and '/wiki/' in album_link['href']:
                                        album_title = album_link.get_text().strip()
                                        album_wiki_url = urljoin(base_url, album_link['href'])
                                        
                                        year = ''
                                        if len(cells) > 1:
                                            year_text = cells[1].get_text()
                                            year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                                            year = year_match.group(0) if year_match else ''
                                        
                                        if not any(a['title'] == album_title for a in albums):
                                            album_info = {
                                                'title': album_title,
                                                'year': year,
                                                'wiki_url': album_wiki_url,
                                                'spotify_url': get_spotify_album_url(album_title, wiki_url),
                                                'spotify_image': '',
                                                'youtube_url': ''
                                            }
                                            albums.append(album_info)
                                            print(f"アルバム追加: {album_title} ({year})")
                        current = current.find_next_sibling()
                    
                    if albums:
                        break
            
            # パターン2: <p><b>Studio albums</b></p>形式（リスト形式）
            if not studio_albums_found or len(albums) == 0:
                print("見出し形式で見つからなかったため、リスト形式を探索...")
                # Discographyセクションを探す
                for heading in content.find_all(['h2', 'h3']):
                    heading_text = heading.get_text().lower()
                    if 'discography' in heading_text or 'ディスコグラフィ' in heading_text:
                        print(f"Discographyセクションを発見: {heading.get_text()}")
                        
                        # h2が<div class="mw-heading">でラップされている場合を考慮
                        # 親要素から次の要素を探す
                        parent = heading.parent
                        print(f"親要素: {parent.name if parent else 'None'}, クラス: {parent.get('class', []) if parent else 'None'}")
                        
                        # 親がdiv.mw-headingの場合、その次の要素から探索
                        if parent and parent.name == 'div' and 'mw-heading' in parent.get('class', []):
                            current = parent.find_next_sibling()
                            print(f"親要素の次の要素から探索開始: {current.name if current else 'None'}")
                        else:
                            current = heading.find_next_sibling()
                            print(f"h2の次の要素から探索開始: {current.name if current else 'None'}")
                        
                        # Discographyセクション内でStudio albumsを探す
                        checked_count = 0
                        while current and checked_count < 50:  # 無限ループ防止
                            checked_count += 1
                            
                            # 次のh2セクションに到達したら終了
                            if current.name == 'div' and 'mw-heading' in current.get('class', []):
                                next_h2 = current.find('h2')
                                if next_h2:
                                    print(f"次のh2セクションに到達: {next_h2.get_text()}")
                                    break
                            
                            # <p><b>Studio albums</b></p>パターンを探す
                            if current.name == 'p':
                                bold_tag = current.find(['b', 'strong'])
                                if bold_tag:
                                    text = bold_tag.get_text().lower()
                                    print(f"太字テキストを発見: {text}")
                                    if 'studio album' in text:
                                        print(f"Studio albums（太字）を発見！")
                                        studio_albums_found = True
                                        
                                        # 次のul要素を探す
                                        next_elem = current.find_next_sibling()
                                        print(f"次の要素: {next_elem.name if next_elem else 'None'}")
                                        
                                        if next_elem and next_elem.name == 'ul':
                                            print("リスト形式のアルバム情報を抽出中...")
                                            li_elements = next_elem.find_all('li', recursive=False)
                                            print(f"li要素数: {len(li_elements)}")
                                            
                                            for li in li_elements:
                                                # リンクを探す
                                                album_link = li.find('a', href=True)
                                                if album_link and '/wiki/' in album_link['href']:
                                                    album_title = album_link.get_text().strip()
                                                    album_wiki_url = urljoin(base_url, album_link['href'])
                                                    
                                                    # 年を抽出（括弧内の年）
                                                    li_text = li.get_text()
                                                    year_match = re.search(r'\((\d{4})\)', li_text)
                                                    year = year_match.group(1) if year_match else ''
                                                    
                                                    if not any(a['title'] == album_title for a in albums):
                                                        album_info = {
                                                            'title': album_title,
                                                            'year': year,
                                                            'wiki_url': album_wiki_url,
                                                            'spotify_url': get_spotify_album_url(album_title, wiki_url),
                                                            'spotify_image': '',
                                                            'youtube_url': ''
                                                        }
                                                        albums.append(album_info)
                                                        print(f"アルバム追加: {album_title} ({year})")
                                                else:
                                                    print(f"リンクが見つからないli: {li.get_text()[:50]}")
                                        break
                            
                            current = current.find_next_sibling()
                        
                        print(f"チェックした要素数: {checked_count}")
                        if studio_albums_found:
                            break
            
            if not studio_albums_found:
                print("Studio albumsセクションが見つかりませんでした")
    
    except Exception as e:
        print(f"アルバム取得エラー: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"取得したアルバム数: {len(albums)}")
    return albums


def get_spotify_album_url(album_title, artist_wiki_url):
    """アルバムタイトルからSpotify URLを検索（簡易版）"""
    # 注: 実際のSpotify API実装が必要
    # ここでは仮のURLを返す
    return f"https://open.spotify.com/search/{quote(album_title)}"


def get_spotify_image_url(spotify_url):
    """Spotify URLから画像URLを取得"""
    # 注: 実際のSpotify API実装またはスクレイピングが必要
    # ここでは空文字列を返す
    return ""
