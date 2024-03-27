from django.http import HttpResponse
from base64 import b64decode

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 特定のパスに対するリクエストに対してのみBasic認証を適用
        if request.path.startswith('/vision/'):
            # HTTP_AUTHORIZATIONヘッダーが存在するかチェック
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                # Basic認証の形式が正しいかチェック
                if len(auth) == 2 and auth[0].lower() == "basic":
                    username, password = b64decode(auth[1]).decode('utf-8').split(':', 1)
                    # 指定されたユーザー名とパスワードで認証
                    if username == 'fugafuga' and password == 'hogehoge1234':
                        return self.get_response(request)

            # 認証に必要な情報がない、または認証が失敗した場合
            response = HttpResponse("Authorization required", status=401)
            response['WWW-Authenticate'] = 'Basic realm="My Realm"'
            return response

        # その他のリクエストは通常通り処理
        return self.get_response(request)
