# Google Calendar API 設定手順

## 1. Google Cloud Console での設定

1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成または既存プロジェクトを選択
3. 左側メニューから「APIとサービス」→「ライブラリ」を選択
4. 「Google Calendar API」を検索して有効化
5. 「認証情報」→「認証情報を作成」→「OAuth 2.0 クライアント ID」を選択
6. アプリケーションの種類で「デスクトップアプリケーション」を選択
7. 名前を入力（例：「Diary App」）して作成
8. JSONファイルをダウンロード

## 2. 認証情報ファイルの配置

1. ダウンロードしたJSONファイルを `credentials.json` という名前に変更
2. プロジェクトの `projects/` フォルダに配置：
   ```
   /Users/okadatoshihiro/Desktop/01_develop/synapseai/projects/credentials.json
   ```

## 3. 初回認証

1. アプリケーションを実行すると、ブラウザが自動で開きます
2. Googleアカウントでログインし、カレンダーへのアクセスを許可
3. 認証完了後、`token.pickle` ファイルが自動生成されます

## 4. ファイル構成

```
projects/
├── credentials.json  # Google APIの認証情報（手動配置）
├── token.pickle      # アクセストークン（自動生成）
└── ...
```

## 5. 注意事項

- `credentials.json` は機密情報です。GitHubなどにアップロードしないでください
- `.gitignore` に以下を追加することを推奨：
  ```
  credentials.json
  token.pickle
  ```

## 6. テスト

1. Djangoサーバーを起動：`python manage.py runserver`
2. diary アプリにアクセス
3. 「SYNC CALENDAR」ボタンをクリックしてカレンダー情報を確認

## 7. エラーが発生した場合

- `credentials.json` ファイルの存在を確認
- Google Calendar APIが有効化されているか確認
- OAuth 2.0 クライアント IDが正しく設定されているか確認
- ブラウザでGoogle認証が完了しているか確認
