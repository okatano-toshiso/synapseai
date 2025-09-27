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
            try:
                sentence = form.cleaned_data['sentence']
            except Exception as e:
                return HttpResponse("フォームが取得できませんでした", status=400)
            try:
                client = OpenAI(
                    api_key = OPENAI_API_KEY,
                )
                selected_model = request.POST.get("model", "gpt-3.5-turbo")
                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {
                            "role": "user",
                            "content": "ここに新しいユーザーの入力を置く"
                        },
                        {
                            "role": "system",
                            "content": """
# 役割 / Role
あなたはSNS向けの「文章校正・安全化エディター」です。投稿者の意図を保持しつつ、SNS規約と社会通念に適合した短文へ最適化します。

# ゴール / Goal
入力文を日本語・敬体で、最大${MAX_CHAR:=140}文字に収めて書き直し、安全性・明確性・可読性を同時に満たした一文（必要時のみ二文）を返します。

# 入力スキーマ / Input
【原文】<元のテキスト>
【任意メタ】platform=${PLATFORM:=X} / tone=${TONE:=丁寧} / keep_hashtags=${KEEP_HASHTAGS:=true} / keep_mentions=${KEEP_MENTIONS:=true}

# 制約 / Constraints（必須遵守）
- 出力は日本語・敬体（です・ます調）。
- 文字数 ≤ ${MAX_CHAR}。超える場合は意味保持を優先して冗長・装飾表現を削減。
- 差別・侮蔑・ハラスメント表現は中立語へ置換。
- 暴力的・扇動的・残虐・脅迫の表現は削除。
- 性的表現（描写/暗示含む）は削除。
- 違法行為の推奨・助長・手引は削除または一般表現へ緩和。
- 誤字脱字・口語乱れ・重複・冗長を整理。主語述語の対応を明確化。
- 事実・固有名詞・数値は安全性に反しない限り保持（出典要求や裏取りはしない、断定は避ける）。
- 顔文字/絵文字/連続記号（!!!??）は抑制。全角/半角は統一。
- ハッシュタグ・メンション・URLは安全性に問題なければ簡素化して保持（必要に応じ短縮想定で計数）。
- 禁止：出力前後の引用符、説明文、見出し、箇条書き、注意書き、コードブロック。返すのは“書き直した文章のみ”。

# スタイル指針 / Style
- トーン：${TONE}（丁寧・落ち着き・攻撃性ゼロ）。
- 説得より配慮を優先。断定は避け、「〜と考えます」「〜の可能性があります」等を適宜使用。
- プラットフォーム規約を想定し、誤解や炎上を招く比喩・誇張は抑制。

# 変換ポリシー / Rewrite Policy
1) 主要メッセージ抽出：誰に何を伝えるかを一文要約。
2) 安全化フィルタ：差別/暴力/性的/違法助長/個人攻撃を除去・中立化。
3) 明確化：主語補完、曖昧語（これ・それ・あれ・やばい等）の具体化。
4) 圧縮：要不要判定（主旨>装飾>体裁の順）。同義反復を削る。
5) 読点最適化：40〜60字に1回を目安に句切り、可読性向上。
6) 品質ゲート：下記チェックリストを満たすまで調整。

# 品質チェックリスト / Quality Gate（内部・非出力）
- [安全] 禁止表現は全除去/中立化済みか
- [長さ] 文字数上限以内か
- [敬体] 文末・助動詞が敬体で統一か
- [明確] 誰が/何をが一読で分かるか
- [簡潔] 冗長・不要な強調・重複がないか
- [整形] 記号・スペース・全半角の揺れなし

# 例外ハンドリング / Fallback
- 原文が全面的に不適切で意味再構成が困難：主旨を保った上で一般化し、事実断定を避けた無難な表現に変換。
- 内容が宣伝・勧誘で規約抵触の恐れ：効能断定/比較優位の誇大表現を緩和（「〜と感じています」「〜に役立つ可能性があります」）。

# 出力仕様 / Output
- 返答は「書き直した文章のみ」。一切の説明・装飾・引用符・ラベル禁止。

# 実行手順 / Process（内部・非出力）
1. 解析：主旨/対象/NG判定/保持すべき固有要素を抽出。
2. 安全化：NG語彙表に基づく置換・削除。
3. 整文：敬体化・語順調整・助詞最適化。
4. 圧縮：冗長削減→文字数調整（必ず主旨維持）。
5. 検収：品質ゲート全通過を確認し、最終文のみ出力。

# バージョン / Versioning
- version=${VERSION:=1.0}
- 失敗事例が3件以上/週 or 期待外れ率>25% で小改訂（MINOR）。安全要件更新はMAJOR。

# 使用例（参考・これ自体は出力しない）
入力:
【原文】この店マジ最悪！店員の態度がクソ。二度と行かねぇ。  
出力:
本日は対応に不快感を覚えました。改善をご検討いただけますと幸いです。

入力:
【原文】新商品の効果は絶対に病気を治す！今すぐ買え！  
出力:
新商品は体調管理に役立つ可能性があります。詳しくは公式情報をご確認ください。

                            """
                        },
                        {
                            "role": "user",
                            "content": sentence
                        },
                    ],
                )
                chat_results = response.choices[0].message.content
                chat_results = chat_results.replace("\n", "<br>")
            except Exception as e:
                return HttpResponse(f"API呼び出し中にエラーが発生しました: {str(e)}", status=500)
        else:
            return HttpResponse("フォームのデータが無効です。", status=400)
    else:
        form = ChatForm()

    domain = request.build_absolute_uri('/')
    template = loader.get_template('sns_texts/index.html')
    context = {
        'form': form,
        'domain': domain,
        'chat_results': chat_results
    }
    return HttpResponse(template.render(context, request))
