from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .forms import ChatForm
from .models import RaceInfo
import csv
import io

import os
from openai import OpenAI

# ライブラリの読み込み
import pandas as pd
import urllib
import requests
import re
import chardet

def index(request):
    try:
        OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    except KeyError:
        return HttpResponse("APIキーが設定されていません。", status=500)
    chat_results = ""
    if request.method == "POST":
        form = ChatForm(request.POST, request.FILES)
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

            csv_file = request.FILES['csv_file']
            data_set = csv_file.read()
            result = chardet.detect(data_set)
            encoding = result['encoding']
            data_set = data_set.decode(encoding)
            io_string = io.StringIO(data_set)
            races_info = pd.read_csv(io_string)
            # フィルタリング条件を指定
            race_number = form.cleaned_data['race_number']
            location = form.cleaned_data['location']
            horses_info = races_info[
                (races_info['date'] == date) & 
                (races_info['round'] == race_number) & 
                (races_info['location'].str.contains(location))
            ]
            horse_names = races_info['horse'].tolist()
            # フィルタリング結果をコンソールに出力
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                result = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
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
                            {races_info}
                            なお、下記のリストの情報は合わせて検索してください。
                            検索用馬名リスト: {horse_names}
                            検索用サイト:https://dir.netkeiba.com/
                            馬券の種類は{betting}です。馬券の種類あわせた{betting}の予想の組み合わせを10パターンを出力してください。
                            当選確率が高いと思われる順に並べてください。
                            その場合、馬名と馬番で表示してください。解説も予想の後にしてください。
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
