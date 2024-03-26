"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static

urlpatterns = [
    path('', include('top.urls')),
    path('vision/', include('vision.urls')),
    path('lyric_trans/', include('lyric_trans.urls')),
    path('sns_texts/', include('sns_texts.urls')),
    path('chat_app/', include('chat_app.urls')),
    path("polls/", include("polls.urls")),
    path('admin/', admin.site.urls),
    path('chat_bot/', include('chat_bot.urls')),
    path('generate_image/', include('generate_image.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
