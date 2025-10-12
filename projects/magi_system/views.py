from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
from openai import OpenAI

@csrf_exempt
def topic(request):

    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
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

    message = """日本語で応答してください。あなたは優秀なお笑い芸人です。あなたは優秀なお笑い芸人としての意見を述べてください"""
    casper_response = discussion(OPENAI_API_KEY, prompt, message)
    interactions.append({'input': "議論の課題は" + prompt + "です。", 'response': casper_response})

    message = """日本語で応答してください。あなたは優秀なお笑い芸人です。。あなたは優秀なお笑い芸人としての意見を述べてください"""
    balthazar_response = discussion(OPENAI_API_KEY, casper_response, message)
    interactions.append({'input': "議論の課題は" + prompt + "です。", 'response':  balthazar_response})

    message = """日本語で応答してください。あなたは優秀なお笑い芸人です。あなたは優秀なお笑い芸人としての意見を述べてください"""
    melchior_response = discussion(OPENAI_API_KEY, balthazar_response, message)
    interactions.append({'input': "議論の課題は" + prompt + "です。", 'response': melchior_response})

    message = """日本語で応答してください。あなたは結論を出すリーダーです。３つの意見をもとに結論を述べてください"""
    magi_response = discussion(OPENAI_API_KEY, balthazar_response, message)
    interactions.append({'input': "一つ目の意見は「" +  casper_response + "」です。" + "二つ目の意見は「" +  balthazar_response + "」です。" + "三つ目の意見は「" +  melchior_response + "」です。", 'response': magi_response})


    return JsonResponse({'message': interactions})

def magi_discussion(request):
    full_url = request.build_absolute_uri('/')
    app_name = "magi_system"
    return render(request, 'magi.html', {'domain': full_url,'app_name': app_name})
