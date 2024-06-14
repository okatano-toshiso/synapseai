from django.contrib.auth.decorators import login_required
import os
import pandas as pd
import urllib
import requests
import re
from django.http import HttpResponse
from django.template import loader
from django.core.files import File
from django.conf import settings
from .forms import ChatForm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

@login_required
def index(request):
    # メイン処理
    def main(date, race_number, location):
        soup = access_entries()
        location_url = get_location_url(soup)
        round_url = []
        for i in location_url:
            res = requests.get(i)
            soup = BeautifulSoup(res.content, 'html5lib')
            round_url.extend(get_round_url(soup, race_number))
        print(round_url)
        tokyo = riding_ground('東京')
        tokyo.get_weather_condition_info()
        kyoto = riding_ground('京都')
        kyoto.get_weather_condition_info()
        races_info = pd.DataFrame()
        print('レース情報の取得を開始します')
        for i in tqdm(round_url):
            soup = preparing_data(i)
            try:
                races_info = pd.concat([races_info, get_race_info(soup, date, location)])
            except BaseException as err:
                print(err)
                print('予測に必要なデータが掲載されていません')
        current_datetime = datetime.now().strftime('%Y_%m_%d')
        file_name = f"{settings.BASE_DIR}/uploads/jra_scraping/{current_datetime}_data.csv"
        races_info.to_csv(file_name, index=False, encoding='utf-8-sig')
        return races_info
    def access_entries():
        option = Options()
        option.add_argument('--headless')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = ChromeService(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=service, options=chrome_options)
        browser.get('https://www.jra.go.jp/')
        browser.implicitly_wait(20)
        xpath = '//*[@id="quick_menu"]/div/ul/li[2]/a'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()
        xpath = '//*[@id="main"]/div[2]/div/div/div[1]/a'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()
        xpath = '//*[@id="race_list"]/tbody/tr[1]/th'
        elem_search = browser.find_element(By.XPATH, value=xpath)
        elem_search.click()
        cur_url = browser.current_url
        res = requests.get(cur_url)
        soup = BeautifulSoup(res.content, 'lxml')
        return soup
    def get_location_url(soup):
        locations_info = soup.find_all('div', attrs={'class': 'link_list multi div3 center mid narrow'})
        location_url = []
        for locations in locations_info:
            for location in locations.find_all('a'):
                url = urllib.parse.urljoin('https://www.jra.go.jp', location.get('href'))
                location_url.append(url)
        return location_url
    def get_round_url(soup, race_number):
        rounds_info = soup.find('ul', attrs={'class': 'nav race-num mt15'})
        round_url = []
        tmp = rounds_info.find_all('a')
        alt_race = f"{race_number}レース"
        for round in rounds_info.find_all('a'):
            img_tag = round.find('img')
            if img_tag and 'alt' in img_tag.attrs and img_tag.attrs['alt'] ==  alt_race:
                url = urllib.parse.urljoin('https://www.jra.go.jp', round.get('href'))
                round_url.append(url)
        return round_url
    def get_race_info(soup, date, location):
        try:
            race_info = pd.DataFrame()
            # print(race_info)
            tbody = soup.find('tbody')
            tbody = tbody.find_all('tr')
            df = pd.DataFrame()
            # print(df)
            df_tmp1 = pd.DataFrame()
            for tb in tbody[0:]:
                tmp = tb.text.split('\n')
                if '除外' in tmp or '取消' in tmp:
                    continue
                df_tmp1 = pd.Series(tmp)
                df = pd.concat([df, df_tmp1], axis=1)


            horse_age_combined = df.iloc[11] + ' ' + df.iloc[12] + ' ' + df.iloc[13]
            # print(horse_age_combined)
            horse_info_combined = df.iloc[8] + ' ' + df.iloc[9] + ' ' + df.iloc[10]

            horse_number = []
            for i in df.iloc[2]:
                try:
                    match = re.search(r'\d+$', i.strip())
                    if match:
                        horse_number.append(match.group(0))
                    else:
                        horse_number.append(None) 
                except Exception as e:
                    print(f"Error processing horse_number: {e}")

            horse_father = []
            for i in horse_info_combined:
                try:
                    match = re.search(r'父：([^\s]+)', i.strip())
                    if match:
                        horse_father.append(match.group(1))
                    else:
                        horse_father.append(None)
                except Exception as e:
                    print(f"Error processing horse_father: {e}")

            horse_mother = []
            for i in horse_info_combined:
                try:
                    match = re.search(r'母：([^\s\(]+)', i.strip())
                    if match:
                        horse_mother.append(match.group(1))
                    else:
                        horse_mother.append(None)
                except Exception as e:
                    print(f"Error processing horse_mother: {e}")

            horse_mother_father = []
            for i in horse_info_combined:
                try:
                    match = re.search(r'母の父：([^\)]+)', i.strip())
                    if match:
                        horse_mother_father.append(match.group(1))
                    else:
                        horse_mother_father.append(None)
                except Exception as e:
                    print(f"Error processing horse_mother_father: {e}")

            weight_change = []
            for i in df.iloc[7]:
                try:
                    match = re.search(r'\(([-+]?\d+)\)', i)
                    if match:
                        weight_change.append(match.group(0))
                    else:
                        weight_change.append('(0)')
                except Exception as e:
                    print(f"Error processing weight_change: {e}")

            popular_list = []
            for i in df.iloc[5]:
                try:
                    popular = re.findall('\(.*\)', i)
                    if popular:
                        popular = re.sub(r'\D', '', popular[0])
                        popular_list.append(popular)
                    else:
                        popular_list.append(None) 
                except Exception as e:
                    print(f"Error processing popular_list: {e}")

            horse_list = []
            for i in df.iloc[5]:
                try:
                    horse = re.findall('[\u30A1-\u30FF]+', i)[0]
                    if horse:
                        horse_list.append(horse)
                    else:
                        horse_list.append(None) 
                except Exception as e:
                    print(f"Error processing horse_list: {e}")

            odds_list = []
            for i in df.iloc[5]:
                try:
                    tmp = i.split('(')
                    odds = re.sub('[\u30A1-\u30FF]+', '', tmp[0])
                    if odds:
                        odds_list.append(odds)
                    else:
                        odds_list.append(None) 
                except Exception as e:
                    print(f"Error processing odds_list: {e}")

            horse_weight_list = []
            for i in df.iloc[7]:
                try:
                    tmp = i.split('kg')
                    horse_weight = tmp[0]
                    horse_weight = re.search(r'\d+$', horse_weight)
                    if horse_weight:
                        horse_weight = int(horse_weight.group(0))
                        horse_weight_list.append(horse_weight)
                    else:
                        horse_weight_list.append(None)
                except Exception as e:
                    print(f"Error processing horse_weight_list: {e}")

            age_list = []
            for i in horse_age_combined:
                try:
                    tmp = i.split('/')
                    age = tmp[0].replace('せん', 'セ')
                    print(age)
                    if age_list:
                        age_list.append(age)
                    else:
                        age_list.append(None)
                except Exception as e:
                    print(f"Error processing age_list: {e}")

            rider_weight_list = []
            for i in df.iloc[15]:
                try:
                    tmp = i.split('kg')
                    rider_weight = tmp[0]
                    if rider_weight:
                        rider_weight_list.append(rider_weight)
                    else:
                        rider_weight_list.append(None)
                except Exception as e:
                    print(f"Error processing rider_weight_list: {e}")

            rider_list = []
            for i in df.iloc[17]:
                try:
                    rider = i.replace('▲', '').replace('△', '').replace('☆', '').replace('◇', '').replace('★', '').replace(' ', '')
                    if rider:
                        rider_list.append(rider)
                    else:
                        rider_list.append(None)
                except Exception as e:
                    print(f"Error processing rider_list: {e}")

            round = soup.find_all('div', attrs={'class': 'race_number'})
            round = round[0].next_element.attrs['alt']
            round = round.replace('レース', '')
            round = int(round)
            race_base_info = soup.find_all('div', attrs={'class': 'cell date'})
            race_date = race_base_info[0].text.split()[0]
            race_date = race_date.split('（')[0]
            race_location = race_base_info[0].text.split()[1]
            race_location = race_location.replace('日', '日目')
            race_name = soup.find_all('span', attrs={'class': 'race_name'})
            race_name = race_name[0].text
            race_course_info = soup.find_all('div', attrs={'class': 'cell course'})
            race_distance = race_course_info[0].text.split()
            race_distance = re.sub(r'\D', '', race_distance[0])
            ground = str(race_course_info[0].text.split())
            if 'ダート' in ground:
                ground = 'ダート'
            if '芝' in ground:
                ground = '芝'
            if race_date == date and location in race_location:
                print(age_list)
                race_info['number'] = horse_number
                race_info['horse'] = horse_list
                race_info['horse_father'] = horse_father
                race_info['horse_mother'] = horse_mother
                race_info['horse_mother_father'] = horse_mother_father
                race_info['age'] = age_list
                race_info['horse_weight_list'] = horse_weight_list
                race_info['weight_change'] = weight_change
                race_info['rider_weight'] = rider_weight_list
                race_info['rider'] = rider_list
                race_info['odds'] = odds_list
                race_info['popular'] = popular_list
                race_info['distance'] = race_distance
                race_info['ground'] = ground
                race_info['date'] = race_date
                race_info['race_name'] = race_name
                race_info['location'] = race_location
                race_info['round'] = round
                # print(race_info)
                return race_info
            else:
                return false
        except IndexError as e:
            print(f"IndexError in get_race_info: {e}")
        except Exception as e:
            print(f"Unexpected error in get_race_info: {e}")
    def preparing_data(url):
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'html5lib')
        class_blinker_tag = soup.find_all('span', attrs={'class': 'horse_icon blinker'})
        for i in class_blinker_tag:
            i.decompose()
        num_tag = soup.find_all('td', attrs={'class': 'num'})
        for i in soup.find_all('td', attrs={'class': 'num'}):
            num = i.text.replace('\n', '')
            i.replace_with(num)
        return soup
    class riding_ground:
        def __init__(self, location):
            self.location = location
            self.weather = ''
            self.shiba_condition = ''
            self.dart_condition = ''
        def get_weather_condition_info(self):
            url = 'https://www.jra.go.jp/keiba/baba/'
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            class_cell_txt = soup.find('div', attrs={'class': 'cell txt'})
            self.weather = class_cell_txt.text.replace('天候：', '')
            location_list = []
            location_url = []
            class_nav_tab = soup.find_all('div', attrs={'class': 'nav tab'})
            tag_a = class_nav_tab[0].find_all('a')
            for i in tag_a:
                location_list.append(i.text)
                url = urllib.parse.urljoin(url, i.get('href'))
                location_url.append(url)
            location_list = [s.replace('競馬場', '') for s in location_list]
            index_num = location_list.index(self.location)
            url = location_url[index_num]
            res = requests.get(url)
            soup = BeautifulSoup(res.content, 'lxml')
            class_data_list_unit = soup.find_all('div', attrs={'class': 'data_list_unit'})
            for i in class_data_list_unit:
                tag_h4 = i.find_all('h4')
                if len(tag_h4) == 0:
                    continue
                if tag_h4[0].text == '芝':
                    tag_p = i.find_all('p')
                    self.shiba_condition = tag_p[0].text
                if tag_h4[0].text == 'ダート':
                    tag_p = i.find_all('p')
                    self.dart_condition = tag_p[0].text
            return {
                'weather': self.weather,
                'shiba_condition': self.shiba_condition,
                'dart_condition': self.dart_condition
            }
    def set_weather_condition(df, tokyo, kyoto):
        df = df.reset_index(drop=True)
        location_list = df['location']
        ground_list = df['ground']
        weather_list = []
        condition_list = []
        for i, location in enumerate(location_list):
            if '東京' in location:
                weather_list.append(tokyo.weather)
                if '芝' in ground_list[i]:
                    condition_list.append(tokyo.shiba_condition)
                if 'ダート' in ground_list[i]:
                    condition_list.append(tokyo.dart_condition)
            if '京都' in location:
                weather_list.append(kyoto.weather)
                if '芝' in ground_list[i]:
                    condition_list.append(kyoto.shiba_condition)
                if 'ダート' in ground_list[i]:
                    condition_list.append(kyoto.dart_condition)
        df['condition'] = condition_list
        df['weather'] = weather_list
        return df
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            if 'date' in form.cleaned_data and form.cleaned_data['date'] is not None:
                date = form.cleaned_data['date']
                date = date.strftime('%Y年%-m月%-d日')
            else:
                date = ''
            race_number = form.cleaned_data['race_number']
            location = form.cleaned_data['location']
            main(date, race_number, location)
            chat_results = "SUCCESS"
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()
    current_datetime = datetime.now().strftime('%Y_%m_%d')
    domain = request.build_absolute_uri('/')
    template = loader.get_template('jra_scraping/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'jra_scraping',
        'current_datetime': current_datetime,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))

def download_file(request, file_name):
    current_datetime = datetime.now().strftime('%Y_%m_%d')
    file_name = f"{settings.BASE_DIR}/uploads/jra_scraping/{current_datetime}_data.csv"  # f文字列を使用
    print(file_name)
    file_path = os.path.join(file_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        return HttpResponse("File not found.")