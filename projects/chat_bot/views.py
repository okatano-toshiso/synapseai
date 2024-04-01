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
    conversation = request.session.get('conversation', [])
    conversation.append(user_message)
    prompt = " ".join(conversation)
    client = OpenAI(
        api_key = OPENAI_API_KEY,
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
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
    conversation.append(bot_response)
    request.session['conversation'] = conversation
    return JsonResponse({'message': bot_response})
def chat_view(request):
    full_url = request.build_absolute_uri('/')
    app_name = "chat_bot"
    return render(request, 'chat.html', {'domain': full_url,'app_name': app_name})
