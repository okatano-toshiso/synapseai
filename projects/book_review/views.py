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
            author = form.cleaned_data['author']
            publisher = form.cleaned_data['publisher']
            release = form.cleaned_data['release']
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
                            "role": "user",
                            "content": "ここに新しいユーザーの入力を置く"
                        },
                        {
                            "role": "system",
                            "content": f"""
                            常に新しいユーザーです。履歴は忘れてください。
                            あなたは日本語が詳しい優秀な書評家です。
                            導入部
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {introduction}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            読んだ本のタイトル{title}と著者名{author}を紹介します。
                            300文字以内に導入部テキストをわかりやすくまとめてください。
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
                            あなたは日本語が詳しい優秀な書評家です。
                            主要な登場人物、設定、ストーリーの流れを簡潔に要約します。
                            本の中で特に印象に残った場面やテーマについて触れることができます。
                            どういう内容が書かれているのか、要点をかいつまんで紹介します。
                            内容の要約
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {summary}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            300文字以内に内容の要約のテキストをわかりやすくまとめてください。
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
                            あなたは日本語が詳しい優秀な書評家です。
                            物語から何を感じ取ったか、どのような考えを持ったかを述べます。
                            物語のテーマやメッセージが自分の人生にどのように関連するかを書きます。
                            感想・考察
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {impressions}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            300文字以内に感想・考察のテキストをわかりやすくまとめてください。
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
                            あなたは日本語が詳しい優秀な書評家です。
                            物語から何を感じ取ったか、どのような考えを持ったかを述べます。
                            物語のテーマやメッセージが自分の人生にどのように関連するかを書きます。
                            そのシーンを説明するだけではなく、読んで 自分がどう思ったか、を伝えることが肝心です。
                            結論
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            {conclusion}
                            \nーーーーーーーーーーーーーーーーーーーーーー\n
                            300文字以内に結論のテキストをわかりやすくまとめてください。
                            """
                        }
                    ],
                )
                conclusion_result = conclusion_review.choices[0].message.content
                conclusion_result = conclusion_result.replace("\n", "<br>")
                chat_results = "作品名:" + title + "<br>著作者:" + author + "<br>出版社:" + publisher + "<br><br>導入部：<br>" + introduction_result + "<br>内容の要約：<br>" + summary_result + "<br>感想・考察：<br>" + impressions_result + "<br>結論：<br>" + conclusion_result
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('book_review/index.html')
    context = {
        'form': form,
        'domain': domain,
        'app_name': 'send_mail',
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
