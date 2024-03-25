from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from base64 import b64decode

class BasicAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 特定のアプリケーションまたはビューへのリクエストかどうかをチェック
        if request.path.startswith('/vision/'):
            # BASIC認証の処理
            if 'HTTP_AUTHORIZATION' in request.META:
                auth = request.META['HTTP_AUTHORIZATION'].split()
                if len(auth) == 2 and auth[0].lower() == "basic":
                    username, password = b64decode(auth[1]).decode('utf-8').split(':')
                    user = authenticate(request, username=username, password=password)
                    if user is not None and user.is_active:
                        login(request, user)
                        return self.get_response(request)

            # 認証が必要な場合、または認証に失敗した場合
            response = HttpResponse("Authorization required", status=401)
            response['WWW-Authenticate'] = 'Basic realm="My Realm"'
            return response

        # その他のリクエストは通常どおり処理
        return self.get_response(request)
