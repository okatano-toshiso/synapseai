import base64
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from base64 import b64decode

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 特定のパスへのリクエストのみ認証を適用
        if request.path.startswith('/vision/'):
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2:
                    # Basic認証のデコード
                    username, password = base64.b64decode(auth[1]).decode('utf-8').split(':', 1)
                    # 固定のユーザー名とパスワードで認証
                    if username == 'myusername' and password == 'mypassword':
                        return self.get_response(request)

            # 認証に失敗した場合のレスポンス
            response = HttpResponse("Authorization Required", status=401)
            response['WWW-Authenticate'] = 'Basic'
            return response

        return self.get_response(request)