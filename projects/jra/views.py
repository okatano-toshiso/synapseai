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
            # レース場の情報
            rase = form.cleaned_data['rase']
            if 'date' in form.cleaned_data and form.cleaned_data['date'] is not None:
                date = form.cleaned_data['date']
                date = date.strftime('%Y-%m-%d')
            else:
                date = ''
            distance = form.cleaned_data['distance']
            course = form.cleaned_data['course']
            orientation = form.cleaned_data['orientation']
            place = form.cleaned_data['place']
            weather = form.cleaned_data['weather']
            condition = form.cleaned_data['condition']
            betting = form.cleaned_data['betting']
            # 出走馬の情報
            racehorses = []
            for i in range(1, 19):
                num = str(i).zfill(2)  # 01, 02, ..., 18 のように0埋め
                name = form.cleaned_data.get(f'Racehorse_name_{num}')
                if name:  # nameが存在する場合のみ処理を行う
                    racehorse = {
                        'frame': form.cleaned_data.get(f'Racehorse_frame_{num}'),
                        'number': form.cleaned_data.get(f'Racehorse_number_{num}'),
                        'name': name,
                        'gender': form.cleaned_data.get(f'Racehorse_gender_{num}'),
                        'age': form.cleaned_data.get(f'Racehorse_age_{num}'),
                        'jockey': form.cleaned_data.get(f'Racehorse_jockey_{num}'),
                        'weight': form.cleaned_data.get(f'Racehorse_weight_{num}'),
                        'barn': form.cleaned_data.get(f'Racehorse_barn_{num}'),
                        'body': form.cleaned_data.get(f'Racehorse_body_{num}'),
                        'fluctuation': form.cleaned_data.get(f'Racehorse_fluctuation_{num}'),
                        'odds': form.cleaned_data.get(f'Racehorse_odds_{num}')
                    }
                    racehorses.append(racehorse)
                    # 馬名のみ抽出して検索用の文字列を作成
                    horse_names = ", ".join([horse['name'] for horse in racehorses])
                    # プロンプトに出走馬の情報を追加
                    horses_info = "\n".join(
                        [f"枠番号: {horse['frame']}, 馬番: {horse['number']}, 馬名: {horse['name']}, 性別: {horse['gender']}, 年齢: {horse['age']}, 騎手: {horse['jockey']}, 重量: {horse['weight']}, 厩舎: {horse['barn']}, 馬体重: {horse['body']}, 馬体重変動: {horse['fluctuation']}, オッズ: {horse['odds']}" for horse in racehorses]
                    )
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
