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
            rase01 = form.cleaned_data['rase01']
            rase02 = form.cleaned_data['rase02']
            rase03 = form.cleaned_data['rase03']
            rase04 = form.cleaned_data['rase04']
            rase05 = form.cleaned_data['rase05']
            if 'date' in form.cleaned_data and form.cleaned_data['date'] is not None:
                date = form.cleaned_data['date']
                date = date.strftime('%Y-%m-%d')
            else:
                date = ''
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
                            対象日: [{date}]
                            {date}のJRA主催WIN5の予想を行います。各レースの1位となる馬を予測し、10パターンの予想を出力します。
                            1. https://www.netkeiba.com/を開き、{date}の{rase01}の情報を確認してください。
                            2. 各レースの出馬表と過去の成績を参考にして、1位となりそうな馬を選びます。
                            3. https://www.netkeiba.com/を開き、{date}の{rase02}の情報を確認してください。
                            4. 各レースの出馬表と過去の成績を参考にして、1位となりそうな馬を選びます。
                            5. https://www.netkeiba.com/を開き、{date}の{rase03}の情報を確認してください。
                            6. 各レースの出馬表と過去の成績を参考にして、1位となりそうな馬を選びます。
                            7. https://www.netkeiba.com/を開き、{date}の{rase04}の情報を確認してください。
                            8. 各レースの出馬表と過去の成績を参考にして、1位となりそうな馬を選びます。
                            7. https://www.netkeiba.com/を開き、{date}の{rase05}の情報を確認してください。
                            8. 各レースの出馬表と過去の成績を参考にして、1位となりそうな馬を選びます。
                            3. 各レースの1位となる馬の番号を5つずつ、10パターン作成します。
                            パターン回答例:
                            {rase01}の１位の馬名
                            {rase02}の１位の馬名
                            {rase03}の１位の馬名
                            {rase04}の１位の馬名
                            {rase05}の１位の馬名
                            1. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            2. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            3. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            4. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            5. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            6. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            7. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            8. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            9. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            10. [{rase01}の馬番号], [{rase02}の馬番号], [{rase03}の馬番号], [{rase04}の馬番号], [{rase05}の馬番号]
                            パターン回答例に合わせた形式で、回答だけ返してください。回答以外の情報は不要です。
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
    template = loader.get_template('win5/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'jra',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
