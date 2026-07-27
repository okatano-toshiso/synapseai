# E資格 判断トレーナー（Django）

単なる単語カードではなく、以下を記録します。

- 正答・不正解
- 回答時間
- 正答率
- 復習間隔
- 失敗回数
- 3回以上正答したカード数

## 起動

Python 3.14 + Django 6.0 を想定しています。

```bash
cd e_shikaku_cards
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_cards
python manage.py createsuperuser  # 任意
python manage.py runserver
```

ブラウザで `http://127.0.0.1:8000/` を開きます。

## 評価ボタン

- Again: 不正解。10分後に再出題
- Hard: 正解したが迷った。短い間隔
- Good: 3秒程度で即答
- Easy: ほぼ反射で回答

## カード追加

`http://127.0.0.1:8000/admin/` から追加できます。
カードは「即答」「選択肢消去」「数式」「PyTorch対応」の4種類です。

## 学習判定の考え方

「答えを見覚えている」だけでは定着扱いにしません。回答時間、正答率、復習間隔を合わせて判断します。
