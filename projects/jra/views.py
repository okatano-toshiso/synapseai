from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
import os
from openai import OpenAI

# ライブラリの読み込み
import pandas as pd
import urllib
import requests
import re

# スクレイピングで使用するライブラリを読み込む
# from webdriver_manager.chrome import ChromeDriverManager

# from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
# from selenium.webdriver.chrome.options import Options

# プログレスバーを表示するためのライブラリを読み込む
from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait


def index(request):
    # メイン処理
    def main():
        # seleniumで出走表にアクセスする
        soup = access_entries()
        # 開催場所のURLを取得する
        location_url = get_location_url(soup)

        # 開催場所ごとのラウンドのURLを取得する
        round_url = []
        for i in location_url:
            res = requests.get(i)
            soup = BeautifulSoup(res.content, 'html5lib')
            round_url.extend(get_round_url(soup))

        # 天候と馬場情報を取得する
        tokyo = riding_ground('東京')
        tokyo.get_weather_condition_info()

        kyoto = riding_ground('京都')
        kyoto.get_weather_condition_info()

        # レース情報の抽出と整形を行い、データフレームに追記保存する
        races_info = pd.DataFrame()
        print('レース情報の取得を開始します')
        for i in tqdm(round_url):
            soup = preparing_data(i)
            try:
                races_info = pd.concat([races_info, get_race_info(soup)])
            except BaseException as err:
                print(err)
                print('予測に必要なデータが掲載されていません')
        return  races_info
        # print(races_info)
        # 天候、馬場情報を設定する
        # races_info = set_weather_condition(races_info, tokyo, kyoto)

        # CSVにレース情報を保存する
        # file_name = settings.BASE_DIR / "uploads/win5/data.csv"
        # races_info.to_csv(file_name, encoding='utf-8', index=False, errors="ignore")


    # chromeを起動し、jra.go.jpにアクセスして出走表を表示する
    # 直接、https://jra.go.jp/JRADB/accessD.htmlにアクセスするとエラーになるので、seleniumでアクセスする
    # 引数:なし
    # 戻値:BeautifulSoup4オブジェクト
    def access_entries():
        # chromeを起動する
        option = Options()
        option.add_argument('--headless')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # ChromeDriverを設定
        service = ChromeService(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)


        # browser = webdriver.Chrome(ChromeDriverManager().install())
        # 競馬データベースを開く
        browser.get('https://www.jra.go.jp/')
        browser.implicitly_wait(20)  # 指定した要素が見つかるまでの待ち時間を20秒と設定する
        browser.set_page_load_timeout(600)
        wait = WebDriverWait(browser, 600)



        # 出馬表をクリック
        xpath = '//*[@id="quick_menu"]/div/ul/li[2]/a'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()
        # 「今週の出馬表」の左端の開催をクリック
        xpath = '//*[@id="main"]/div[2]/div/div/div[1]/a'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()

        # ラウンドをクリック
        xpath = '//*[@id="race_list"]/tbody/tr[1]/th'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()

        # 表示しているページのURLを取得する
        cur_url = browser.current_url
        res = requests.get(cur_url)  # 指定したURLからデータを取得する
        soup = BeautifulSoup(res.content, 'lxml')  # content形式で取得したデータをhtml形式で分割する

        return soup

    def get_location_url(soup):
        locations_info = soup.find_all('div', attrs={'class': 'link_list multi div3 center mid narrow'})
        # 開催場所のURLを保存するリストを用意
        location_url = []
        # 取得したdivタグから追加でaタグを取得し、aタグからhrefを抽出する
        # 'https://www.jra.go.jp'と抽出したhrefを結合してlocation_urlに保存する
        for locations in locations_info:
            for location in locations.find_all('a'):
                url = urllib.parse.urljoin('https://www.jra.go.jp', location.get('href'))
                location_url.append(url)
        return location_url

    # ラウンドのURLを取得する
    # ラウンドへのリンクはページの上部と下部の2箇所に配置されている
    # 上部のリンクを用いてラウンドのURLを取得する
    # 引数:BeautifulSoupオブジェクト
    # 戻値:ラウンドのURLをリストで返す
    def get_round_url(soup):
        rounds_info = soup.find('ul', attrs={'class': 'nav race-num mt15'})
        # ラウンドのURLを保存するリストを用意
        round_url = []
        tmp = rounds_info.find_all('a')
        # リンクページのURLを作成する
        for round in rounds_info.find_all('a'):
            url = urllib.parse.urljoin('https://www.jra.go.jp', round.get('href'))
            round_url.append(url)
        return round_url

    # レース情報を取得する
    # 引数:BeautifulSoupオブジェクト
    # 戻値:取得したレース情報をデータフレームで返す
    def get_race_info(soup):
        # 出走情報を保存するデータフレームを用意する
        race_info = pd.DataFrame()
        # tableデータを抽出する
        tbody = soup.find('tbody')
        tbody = tbody.find_all('tr')
        # 作業用のデータフレームを用意する
        df = pd.DataFrame()
        df_tmp1 = pd.DataFrame()
        # tableデータを1行ごとにデータフレームに代入する
        # 除外、取消の出走馬は、データフレームに含めない
        for tb in tbody[0:]:
            tmp = tb.text.split('\n')
            if '除外' in tmp or '取消' in tmp:
                continue
            df_tmp1 = pd.Series(tmp)
            df = pd.concat([df, df_tmp1], axis=1)
        # 人気を抽出する
        popular_list = []
        for i in df.iloc[5]:
            popular = re.findall('\(.*\)', i) # 「(x番人気)」を抽出する
            popular = re.sub(r'\D', '', popular[0])  # 数字を抽出する
            popular_list.append(popular)
        # 名前を抽出する
        horse_list = []
        for i in df.iloc[5]:
            horse = re.findall('[\u30A1-\u30FF]+', i)[0]  # カタカナを抽出する
            horse_list.append(horse)
        # 単勝オッズを抽出する
        # 「キリシマラッキー274.6(14番人気)」の場合、「(」で分割して、カタカナを削除すると、
        # 「274.6」が抽出できる
        odds_list = []
        for i in df.iloc[5]:
            tmp = i.split('(')
            odds = re.sub('[\u30A1-\u30FF]+', '', tmp[0])
            odds_list.append(odds)
        # 馬体重を抽出する
        horse_weight_list = []
        for i in df.iloc[7]:
            tmp = i.split('kg')
            horse_weight = tmp[0]
            # int型への変換処理を入れることで、文字列だった場合はエラーを返すようにする
            horse_weight = int(horse_weight[-3:])
            horse_weight_list.append(horse_weight)
        # 性齢を抽出する
        # 'せん'をnetkeibaの'セ'に合わせる
        age_list = []
        for i in df.iloc[13]:
            tmp = i.split('/')
            age = tmp[0].replace('せん', 'セ')
            age_list.append(age)
        # 斤量を抽出する
        # 騎手の斤量増減を示すマークは削除する
        rider_weight_list = []
        for i in df.iloc[15]:
            tmp = i.split('kg')
            rider_weight = tmp[0]
            rider_weight_list.append(rider_weight)
        # 騎手名を抽出する
        rider_list = []
        for i in df.iloc[17]:
            rider = i.replace('▲', '').replace('△', '').replace('☆', '').replace('◇', '').replace('★', '').replace(' ', '')
            rider_list.append(rider)
        # ラウンド数を取得する
        # 'レース'をnetkeibaの' R'に合わせる
        round = soup.find_all('div', attrs={'class': 'race_number'})
        round = round[0].next_element.attrs['alt']
        round = round.replace('レース', '')
        round = int(round)
        # 開催日、開催場を抽出する
        # 開催日のrace_dateに代入する値は、race_base_infoを空白でsplitした「2022年11月19日（土曜）」を
        # 追加で'（'でsplitして、「2022年11月19日」の形式
        # 'x回東京x日'をnetkeibaの'x回東京x日目'に合わせる
        race_base_info = soup.find_all('div', attrs={'class': 'cell date'})
        race_date = race_base_info[0].text.split()[0]
        race_date = race_date.split('（')[0]
        race_location = race_base_info[0].text.split()[1]
        race_location = race_location.replace('日', '日目')
        # レース名を取得する
        race_name = soup.find_all('span', attrs={'class': 'race_name'})
        race_name = race_name[0].text
        # レース距離を取得する
        race_course_info = soup.find_all('div', attrs={'class': 'cell course'})
        race_distance = race_course_info[0].text.split()
        race_distance = re.sub(r'\D', '', race_distance[0])
        # 馬場を取得する
        ground = str(race_course_info[0].text.split())
        if 'ダート' in ground:
            ground = 'ダート'
        if '芝' in ground:
            ground = '芝'
        # 出走情報のデータフレームに'horse_list'を追記する
        race_info['horse'] = horse_list
        # 出走情報のデータフレームに'age'を追記する
        race_info['age'] = age_list
        # 出走情報のデータフレームに'rider_weight'を追記する
        race_info['rider_weight'] = rider_weight_list
        # 出走情報のデータフレームに'rider'を追記する
        race_info['rider'] = rider_list
        # 出走情報のデータフレームに'odds'を追記する
        race_info['odds'] = odds_list
        # 出走情報のデータフレームに'popular'を追記する
        race_info['popular'] = popular_list
        # 出走情報のデータフレームに'horse_weight'を追記する
        race_info['horse_weight'] = horse_weight_list
        # 出走情報のデータフレームに'distance'を追記する
        race_info['distance'] = race_distance
        # 出走情報のデータフレームに'gournd'を追記する
        race_info['ground'] = ground
        # 出走情報のデータフレームに'race_date'を追記する
        race_info['date'] = race_date
        # 出走情報のデータフレームに'race_name'を追記する
        race_info['race_name'] = race_name
        # 出走情報のデータフレームに'race_location'を追記する
        race_info['location'] = race_location
        # 出走情報のデータフレームに'round'を追記する
        race_info['round'] = round
        return race_info
    # 指定したURLからHTML情報を取得し、データを整形する
    # ブリンカーを着用している馬は、他の馬より1つデータが多いため、その後の処理でエラーが出る
    # ブリンカー着用のタグを削除してデータを整える
    # 引数:ラウンドのURL
    # 戻値:BeautifulSoupオブジェクト
    def preparing_data(url):
        res = requests.get(url)  # 指定したURLからデータを取得する
        soup = BeautifulSoup(res.content, 'html5lib')  # lxmlだと失敗するページがあったので、html5libを設定
        # ブリンカー着用のクラスを削除する
        class_blinker_tag = soup.find_all('span', attrs={'class': 'horse_icon blinker'})
        for i in class_blinker_tag:
            i.decompose()
        # ブリンカー着用のタグを削除しても、不要な改行が残るので、改行を空文字で置換する
        num_tag = soup.find_all('td', attrs={'class': 'num'})
        for i in soup.find_all('td', attrs={'class': 'num'}):
            num = i.text.replace('\n', '')
            i.replace_with(num)
        return soup

    # レース開催場所の天候、馬場情報を取得する
    # 引数:レース開催場所の名前(東京、京都、福島、など)
    # 戻値:なし
    class riding_ground:
        def __init__(self, location):
            self.location = location
            self.weather = ''
            self.shiba_condition = ''
            self.dart_condition = ''
        # レース開催場所の天候、馬場状態を取得する
        def get_weather_condition_info(self):
            url = 'https://www.jra.go.jp/keiba/baba/'
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            # 天候の情報を取得する
            class_cell_txt = soup.find('div', attrs={'class': 'cell txt'})
            self.weather = class_cell_txt.text.replace('天候：', '')
            # レース開催予定の馬場と情報が掲載されているURLを取得する
            location_list = []
            location_url = []
            class_nav_tab = soup.find_all('div', attrs={'class': 'nav tab'})
            tag_a = class_nav_tab[0].find_all('a')
            for i in tag_a:
                location_list.append(i.text)
                url = urllib.parse.urljoin(url, i.get('href'))
                location_url.append(url)
            # 「XX競馬場」を「XX」に置換する
            location_list = [s.replace('競馬場', '') for s in location_list]
            # 指定されたレース開催場所の馬場情報URLを抽出する
            index_num = location_list.index(self.location)
            url = location_url[index_num]
            # urlの馬場情報を取得する
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            class_data_list_unit = soup.find_all('div', attrs={'class': 'data_list_unit'})
            for i in class_data_list_unit:
                tag_h4 = i.find_all('h4')
                # h4が存在しない場合、次の処理に進む
                if len(tag_h4) == 0:
                    continue
                if tag_h4[0].text == '芝':
                    tag_p = i.find_all('p')
                    self.shiba_condition = tag_p[0].text
                if tag_h4[0].text == 'ダート':
                    tag_p = i.find_all('p')
                    self.dart_condition = tag_p[0].text
    # 天候と馬場情報を設定する
    # 引数:レース情報、レース名開催場所
    # 戻値:天候と馬場情報を追加したレース情報
    def set_weather_condition(df, tokyo, kyoto):
        # インデックスをリセットする
        df = df.reset_index(drop=True)
        # レース開催場所を抽出する
        location_list = df['location']
        # 馬場の情報を抽出する
        ground_list = df['ground']
        # 馬場情報を保持するリストを用意
        weather_list = []
        # 馬場情報を保持するリストを用意
        condition_list = []
        for i, location in enumerate(location_list):
            if '東京' in location:
                # 天候を設定する
                weather_list.append(tokyo.weather)
                # 馬場情報を設定する
                if '芝' in ground_list[i]:
                    condition_list.append(tokyo.shiba_condition)
                if 'ダート' in ground_list[i]:
                    condition_list.append(tokyo.dart_condition)
            if '京都' in location:
                # 天候を設定する
                weather_list.append(kyoto.weather)
                # 馬場情報を設定する
                if '芝' in ground_list[i]:
                    condition_list.append(kyoto.shiba_condition)
                if 'ダート' in ground_list[i]:
                    condition_list.append(kyoto.dart_condition)
        df['condition'] = condition_list
        df['weather'] = weather_list
        return df

    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            # レース場の情報
            rase = form.cleaned_data['rase']
            if 'date' in form.cleaned_data and form.cleaned_data['date'] is not None:
                date = form.cleaned_data['date']
                date = date.strftime('%Y年%-m月%-d日')
            else:
                date = ''

            distance = form.cleaned_data['location']
            course = form.cleaned_data['course']
            orientation = form.cleaned_data['orientation']
            place = form.cleaned_data['place']
            weather = form.cleaned_data['weather']
            condition = form.cleaned_data['condition']
            betting = form.cleaned_data['betting']

            # 出走馬の情報
            race_number = form.cleaned_data['race_number']
            location = form.cleaned_data['location']
            races_info = main()
            horses_info = races_info[
                (races_info['date'] == date) & 
                (races_info['round'] == race_number) & 
                (races_info['location'].str.contains(location))
            ]
            horse_names = horses_info['horse'].tolist()
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                result = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            あなたは競馬予想の専門家です。ユーザーが提供する詳細なレース情報および出走馬のデータを基に、最適な予想を提供してください。
                            {date}に開催される{rase}の結果を予想してください。
                            過去の{rase}の情報は下記サイトで調べてください。
                            https://dir.netkeiba.com/
                            競馬場は{place}になります。距離は{distance}、コースの種類は{course}です。コースの回りは{orientation}です。
                            天候は{weather}で、馬場の状態は{condition}になります。
                            馬券の種類は{betting}です。馬券の種類あわせた{betting}の予想のみ出力してください。
                            出走馬の情報を下記に記載します。
                            {horses_info}
                            なお、下記のリストの情報は合わせて検索してください。
                            検索用馬名リスト: {horse_names}
                            検索用サイト:https://dir.netkeiba.com/
                            馬券の種類は{betting}です。馬券の種類あわせた{betting}の予想の組み合わせを10パターンを出力してください。
                            当選確率が高いと思われる順に並べてください。
                            その場合、馬名ではなく馬番で表示してください。解説も予想の後にしてください。
                            例
                            馬券の種類
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            馬番-馬番-馬番
                            ーーーーーーーーーーーーーー
                            解説
                            """
                        }
                    ],
                )
                result = result.choices[0].message.content
                chat_results = result.replace("\n", "<br>")

            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('jra/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'jra',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
