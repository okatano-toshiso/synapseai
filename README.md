# 🌐 SynapseAI

> **AI × Django の統合実験プラットフォーム**  
> 自然言語処理・画像生成・音声認識・チャットボットなど、複数の AI 技術を統合した Web アプリケーション群。

---

## 📖 目次

- [概要](#-概要)
- [主なアプリケーション](#-主なアプリケーション)
- [環境構築手順](#-環境構築手順)
- [ディレクトリ構成](#-ディレクトリ構成)
- [使用技術](#-使用技術)
- [ライセンス](#-ライセンス)
- [作者](#-作者)

---

## 🧠 概要

**SynapseAI** は、AI 技術を活用した Django ベースの統合開発環境です。  
自然言語処理、画像生成、音声認識、翻訳、レビュー分析など、複数の AI アプリを一元的に管理・実行できます。

このリポジトリは Django プロジェクト構成であり、`projects/` ディレクトリ配下に多数のアプリが存在します。  
各アプリは独立した機能を持ち、共通の `core` 設定を通じて統合されています。

---

## 🚀 主なアプリケーション

| アプリ名 | 機能概要 |
|-----------|-----------|
| **chat_app** | シンプルなチャットアプリ。ユーザー間のメッセージ送受信を実装。 |
| **chat_bot** | AI チャットボット機能。自然言語応答を生成。 |
| **chat_interaction** | チャット履歴や対話データの管理。 |
| **sns_texts** | SNS 投稿文の生成・分析。 |
| **generate_image** | テキストから画像を生成する AI モデルを利用。 |
| **lyric_trans** | 歌詞翻訳アプリ。英語⇄日本語の翻訳をサポート。 |
| **book_review / movie_review / music_review** | 書籍・映画・音楽のレビュー投稿・分析。 |
| **diary** | 日記アプリ。感情分析や自動要約機能を搭載可能。 |
| **english** | 英語学習支援アプリ。単語帳や例文生成など。 |
| **callcenter / response_mail / send_mail** | メール送信・自動応答・コールセンター支援機能。 |
| **vision / tts / whispar** | 画像認識、音声合成、音声認識などの AI モジュール。 |
| **jra / jra_scraping / win5** | 競馬データのスクレイピング・分析。 |
| **magi_system** | システム統合・管理用アプリ。 |
| **icon / assets / static** | 静的ファイル・UI コンポーネント管理。 |

---

## ⚙️ 環境構築手順

### 1️⃣ 仮想環境の作成と起動

```bash
conda activate
python -m venv synapse
source synapse/bin/activate
python3 -m pip install --upgrade pip
pip install django
pip freeze > requirements.txt
pip install -r requirements.txt
cd projects
```

### 2️⃣ サーバー起動

```bash
python manage.py runserver
```

### 3️⃣ 仮想環境の停止

```bash
deactivate
```

### 4️⃣ 新規アプリ作成

```bash
python manage.py startapp {myapp}
```

### 5️⃣ 別環境での起動（例: test 環境）

```bash
source test/bin/activate
```

### 6️⃣ 静的ファイルの収集

```bash
python manage.py collectstatic --noinput
```

---

## 📂 ディレクトリ構成

```
projects/
├── core/                # Django プロジェクト設定
├── chat_app/            # チャットアプリ
├── chat_bot/            # AI チャットボット
├── sns_texts/           # SNS テキスト生成
├── generate_image/      # 画像生成
├── lyric_trans/         # 歌詞翻訳
├── diary/               # 日記アプリ
├── english/             # 英語学習
├── vision/              # 画像認識
├── tts/                 # 音声合成
├── whispar/             # 音声認識
└── ...                  # その他のアプリ
```

---

## 🧩 使用技術

- **フレームワーク**: Django (Python)
- **データベース**: SQLite / PostgreSQL
- **フロントエンド**: HTML, CSS, JavaScript
- **AI モジュール**: OpenAI API, Whisper, Stable Diffusion など（予定含む）
- **環境管理**: conda / venv
- **静的ファイル管理**: collectstatic

---

## 📜 ライセンス

このリポジトリの内容は開発者の研究・学習目的で作成されています。  
商用利用や再配布を行う場合は、著作権者の許可を得てください。

---

## 👤 作者

**Toshihiro Okada**  
📧 Email: *[非公開]*  
🌐 GitHub: [okatano-toshiso](https://github.com/okatano-toshiso)

---

> 💡 **参考資料**  
> - [GitHub Docs: Basic writing and formatting syntax](https://docs.github.com/ja/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)  
> - [Reddit: GitHub README Templates](https://www.reddit.com/r/programming/comments/l0mgcy/github_readme_templates_creating_a_good_readme_is/?tl=ja)  
> - [Qiita: READMEの書き方](https://qiita.com/dfalcon0001/items/843b93d90f21b9e99d50)  
> - [C++ Learning: READMEの作り方](https://cpp-learning.com/readme/)
