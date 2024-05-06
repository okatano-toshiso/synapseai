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
            title = form.cleaned_data['title']
            director = form.cleaned_data['director']
            playwright = form.cleaned_data['playwright']
            distributing = form.cleaned_data['distributing']
            music = form.cleaned_data['music']
            casts = form.cleaned_data['casts']
            release = form.cleaned_data['release']
            release = release.strftime('%Y-%m-%d')
            introduction = form.cleaned_data['introduction']
            summary = form.cleaned_data['summary']
            impressions = form.cleaned_data['impressions']
            conclusion = form.cleaned_data['conclusion']
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                introduction_review = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            導入部
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {introduction}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            この映像作品を読んだきっかけを書いてありますので、300文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                introduction_result = introduction_review.choices[0].message.content
                introduction_result = introduction_result.replace("\n", "<br>")
                summary_review = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            あなたは日本語が詳しい優秀な映像作品評論家です。
                            内容の要約
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {summary}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            主要な登場人物、設定、ストーリーの流れを簡潔に要約してあります。
                            映像作品の中で特に印象に残った場面やテーマについて触れています。
                            この映像作品の要約を書いてありますので、300文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                summary_result = summary_review.choices[0].message.content
                summary_result = summary_result.replace("\n", "<br>")

                impressions_review = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            あなたは日本語が詳しい優秀な映像作品評論家です。
                            感想・考察
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {impressions}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            物語から何を感じ取ったか、どのような考えを持ったかのかが書かれています。
                            この映像作品の感想・考察を書いてありますので、300文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                impressions_result = impressions_review.choices[0].message.content
                impressions_result = impressions_result.replace("\n", "<br>")

                conclusion_review = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": f"""
                            あなたは日本語が詳しい優秀な像作品評論家です。
                            結論
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {conclusion}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            物語から何を感じ取ったか、どのような考えを持ったかを述べています。
                            物語のテーマやメッセージが自分の人生にどのように活かしていくかを書いています。
                            この映像作品の結論を書いてありますので、300文字以内に綺麗に校正してまとめてください。
                            """
                        }
                    ],
                )
                conclusion_result = conclusion_review.choices[0].message.content
                conclusion_result = conclusion_result.replace("\n", "<br>")
                casts = casts.replace("\n", "<br>")
                chat_results = "作品名:" + title + "<br>監督:" + director + "<br>脚本家:" + playwright + "<br>配給会社:" + distributing + "<br>公開日:" + release + "<br>主題歌:" + music + "<br><br>出演者:<br>" + casts + "<br><br>導入部：<br>" + introduction_result + "<br><br>内容の要約：<br>" + summary_result + "<br><br>感想・考察：<br>" + impressions_result + "<br><br>結論：<br>" + conclusion_result

            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('movie_review/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
