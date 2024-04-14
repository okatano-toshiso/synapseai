from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI

@csrf_exempt
def topic(request):

    OPENAI_API_KEY = os.environ['OPENAI_API_IMAGE_KEY']
    prompt = request.POST.get('message')
    interactions = []

    def discussion(OPENAI_API_KEY, prompt, message):
        client = OpenAI(
            api_key = OPENAI_API_KEY,
        )
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": message
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            temperature=0.3,
            max_tokens=512
        )
        response = response.choices[0].message.content
        response = response.replace("\n", "<br>")
        return response

    message = """日本語で応答してください。あなたは議論に対して、肯定的な意見を主張する役割です。500文字前後で主張してください"""
    casper_response = discussion(OPENAI_API_KEY, prompt, message)
    interactions.append({'input': "議論の課題は" + prompt + "です。", 'response': casper_response})

    message =  """日本語で応答してください。あなたは意見に対して、反論意見を主張する役割です。500文字前後で主張してください"""
    balthazar_response = discussion(OPENAI_API_KEY, casper_response, message)
    interactions.append({'input': casper_response, 'response':  balthazar_response})

    message = """日本語で応答してください。あなたは意見に対して、意見まとめる役割です。500文字前後で、まとめた意見を主張してください"""
    melchior_response = discussion(OPENAI_API_KEY, balthazar_response, message)
    interactions.append({'input': balthazar_response, 'response': melchior_response})

    return JsonResponse({'message': interactions})

def discussion(request):
    full_url = request.build_absolute_uri('/')
    app_name = "chat_interaction"
    return render(request, 'interaction.html', {'domain': full_url,'app_name': app_name})
