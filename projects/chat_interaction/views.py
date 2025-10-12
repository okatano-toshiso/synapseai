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
    model1 = request.POST.get('model1', 'gpt-4')
    model2 = request.POST.get('model2', 'gpt-4')
    model3 = request.POST.get('model3', 'gpt-4')
    role1 = request.POST.get('role1', 'scientist')
    role2 = request.POST.get('role2', 'scientist')
    role3 = request.POST.get('role3', 'scientist')
    interactions = []
    
    # 役割に応じたプロンプトを取得する関数
    def get_role_prompt(role, position):
        # 役割ファイルのマッピング
        role_files = {
            'scientist': 'scientist.txt',
            'parent': 'parent.txt',
            'doctor': 'doctor.txt',
            'teacher': 'teacher.txt',
            'professor': 'professor.txt',
            'police': 'police.txt',
            'lawyer': 'lawyer.txt',
            'criminal': 'criminal.txt',
            'left_wing': 'left_wing.txt',
            'right_wing': 'right_wing.txt',
            'athlete': 'athlete.txt',
            'warlord': 'warlord.txt'
        }
        
        # プロンプトファイルのパス
        base_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file = os.path.join(base_dir, 'prompts', role_files.get(role, 'scientist.txt'))
        
        # ファイルからプロンプトを読み込む
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                base_prompt = f.read().strip()
        except FileNotFoundError:
            base_prompt = ''
        
        # 位置に応じたプロンプトを追加
        if position == 1:
            return base_prompt + "\n\n日本語で応答してください。あなたは議論に対して、肯定的な意見を主張する役割です。500文字前後で主張してください"
        elif position == 2:
            return base_prompt + "\n\n日本語で応答してください。あなたは意見に対して、反論意見を主張する役割です。500文字前後で主張してください"
        elif position == 3:
            return base_prompt + "\n\n日本語で応答してください。あなたは意見に対して、意見まとめる役割です。500文字前後で、まとめた意見を主張してください"
        return base_prompt


    def get_ai_response(OPENAI_API_KEY, prompt, message, model):
        client = OpenAI(api_key=OPENAI_API_KEY)

        messages = [
            {"role": "system", "content": message},
            {"role": "user", "content": prompt},
        ]

        # モデル名を小文字化して判定
        model_lower = model.lower()
        if "gpt-4o" in model_lower or "gpt-4.1" in model_lower:
            max_param = {"max_completion_tokens": 512}
        else:
            max_param = {"max_tokens": 512}

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # temperature=0.3
            # **max_param
        )

        result = response.choices[0].message.content
        return result.replace("\n", "<br>")
    # def get_ai_response(OPENAI_API_KEY, prompt, message, model):
    #     client = OpenAI(
    #         api_key = OPENAI_API_KEY,
    #     )
    #     max_param = {"max_completion_tokens": 512} if any(
    #         key in model for key in ["gpt-4o", "gpt-4.1"]
    #     ) else {"max_tokens": 512}
    #     response = client.chat.completions.create(
    #         model=model,
    #         messages=[
    #             {
    #                 "role": "system",
    #                 "content": message
    #             },
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             },
    #         ],
    #         temperature=0.3,
    #         **max_param
    #     )
    #     response = response.choices[0].message.content
    #     response = response.replace("\n", "<br>")
    #     return response

    message = get_role_prompt(role1, 1)
    casper_response = get_ai_response(OPENAI_API_KEY, prompt, message, model1)
    interactions.append({'input': "議論の課題は" + prompt + "です。", 'response': casper_response})

    message = get_role_prompt(role2, 2)
    balthazar_response = get_ai_response(OPENAI_API_KEY, casper_response, message, model2)
    interactions.append({'input': casper_response, 'response':  balthazar_response})

    message = get_role_prompt(role3, 3)
    melchior_response = get_ai_response(OPENAI_API_KEY, balthazar_response, message, model3)
    interactions.append({'input': balthazar_response, 'response': melchior_response})

    return JsonResponse({'message': interactions})

# def discussion(request):
# chat_interaction/views.py
def chat_interaction_discussion(request):

    full_url = request.build_absolute_uri('/')
    app_name = "chat_interaction"
    return render(request, 'interaction.html', {'domain': full_url,'app_name': app_name})

@csrf_exempt
def reset_chat(request):
    # セッションを完全にクリア
    request.session.flush()
    return JsonResponse({'status': 'reset'})