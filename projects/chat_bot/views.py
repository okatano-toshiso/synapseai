from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI

@csrf_exempt
def ask(request):
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
    user_message = request.POST.get('message')
    selected_model = request.POST.get('model', 'gpt-3.5-turbo')  # デフォルトはgpt-3.5-turbo
    conversation = request.session.get('conversation', [])
    conversation.append(user_message)
    prompt = " ".join(conversation)
    client = OpenAI(
        api_key = OPENAI_API_KEY,
    )
    response = client.chat.completions.create(
        model=selected_model,
        messages=[
            {
                "role": "system",
                "content": "日本語で応答してください"
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
    )
    bot_response = response.choices[0].message.content
    bot_response = bot_response.replace("\n", "<br>")
    # モデル名を語尾に追加
    bot_response_with_model = f"{bot_response}<br><br><small style='color: #888;'>（{selected_model}）</small>"
    conversation.append(bot_response)
    request.session['conversation'] = conversation
    return JsonResponse({'message': bot_response_with_model})
def chat_view(request):
    full_url = request.build_absolute_uri('/')
    app_name = "chat_bot"
    return render(request, 'chat.html', {'domain': full_url,'app_name': app_name})
