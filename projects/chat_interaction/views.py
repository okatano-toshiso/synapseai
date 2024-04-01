from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI

@csrf_exempt
def topic(request):

    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    user_message = request.POST.get('message')
    print(user_message)
    interactions = []

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
                "content": """
                    日本語で応答してください
                    課題に対して1000文字以内で主張してください
                """
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
        max_tokens=1024
    )
    casper_response = response.choices[0].message.content
    casper_response = casper_response.replace("\n", "<br>")
    interactions.append({'input': user_message, 'response': casper_response})
    conversation.append(casper_response)
    request.session['conversation'] = conversation
    # return JsonResponse({'message': casper_response})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "日本語で応答してください。1000文字以内で反論してください。"
            },
            {
                "role": "user",
                "content": casper_response
            },
        ],
        temperature=0.7,
        max_tokens=1024
    )
    balthazar_response = response.choices[0].message.content
    balthazar_response = balthazar_response.replace("\n", "<br>")
    interactions.append({'input': casper_response, 'response': balthazar_response})
    conversation.append(balthazar_response)
    request.session['conversation'] = conversation

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "日本語で応答してください。1000文字以内でまとめてください。"
            },
            {
                "role": "user",
                "content": balthazar_response
            },
        ],
        temperature=0.7,
        max_tokens=1024
    )
    melchior_response = response.choices[0].message.content
    melchior_response = melchior_response.replace("\n", "<br>")
    interactions.append({'input': balthazar_response, 'response': melchior_response})
    conversation.append(melchior_response)
    request.session['conversation'] = conversation
    print(interactions)
    return JsonResponse({'message': interactions})



def discussion(request):
    full_url = request.build_absolute_uri('/')
    app_name = "chat_interaction"
    return render(request, 'interaction.html', {'domain': full_url,'app_name': app_name})
