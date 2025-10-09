import os
import time
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import BondDocument
from .forms import BondDocumentUploadForm
import pdfplumber
from PIL import Image
import io
from openai import OpenAI
import difflib
import google.generativeai as genai
from anthropic import Anthropic


def extract_text_from_pdf_ocr(file_path):
    """PDFからテキストを抽出（pdfplumber）"""
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"PDF解析エラー: {str(e)}")


def extract_text_from_image_tesseract(file_path):
    """画像からテキストを抽出（Tesseract OCR）"""
    try:
        import pytesseract
        image = Image.open(file_path)
        
        # 画像情報を取得
        info = f"画像ファイル情報:\n"
        info += f"形式: {image.format}\n"
        info += f"サイズ: {image.size}\n"
        info += f"モード: {image.mode}\n\n"
        
        # OCRでテキスト抽出（日本語 + 英語）
        info += "=== OCR抽出結果（Tesseract） ===\n\n"
        
        # 日本語と英語の両方で試行
        text_jpn = pytesseract.image_to_string(image, lang='jpn')
        text_eng = pytesseract.image_to_string(image, lang='eng')
        
        if text_jpn.strip():
            info += "[日本語認識]\n"
            info += text_jpn.strip() + "\n\n"
        
        if text_eng.strip() and text_eng.strip() != text_jpn.strip():
            info += "[英語認識]\n"
            info += text_eng.strip()
        
        return info if info else "テキストが検出されませんでした。"
    except Exception as e:
        raise Exception(f"Tesseract OCRエラー: {str(e)}")


def extract_text_with_openai_vision(file_path, file_type, model_name="gpt-4o", instruction_prompt=None):
    """OpenAI Vision APIでテキスト抽出と債券書類分析"""
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # 画像をbase64エンコード
        if file_type == 'pdf':
            # PDFの場合は最初のページを画像に変換
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=1)
            if images:
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                base64_image = base64.b64encode(img_byte_arr).decode('utf-8')
            else:
                raise Exception("PDFから画像への変換に失敗しました")
        else:
            # 画像の場合
            with open(file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 指示プロンプトが指定されていない場合はデフォルト値を使用
        if instruction_prompt is None:
            prompt_text = """この画像を詳細に分析して、以下の情報を抽出してください：

1. 画像に含まれる全てのテキスト（日本語・英語含む）
2. 債券書類の種類（もし債券関連書類の場合）
3. 重要な情報（金額、日付、名称など）
4. 書類の適正性評価

分析結果を構造化された形式で提供してください。"""
        else:
            prompt_text = instruction_prompt
        
        # OpenAI Vision APIで分析
        # o1モデルはvision機能が異なるため、テキストのみの分析を行う
        if model_name.startswith("o1"):
            # o1モデルの場合は画像を直接処理できないため、エラーを返す
            # 将来的にo1がvisionをサポートした場合はここを更新
            raise Exception(f"{model_name}モデルは現在vision機能に対応していません")
        else:
            # gpt-5モデルの場合はmax_completion_tokensを使用
            if model_name.startswith("gpt-5"):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt_text
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_completion_tokens=2000
                )
            else:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt_text
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=2000
                )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI Vision API ({model_name}) エラー: {str(e)}")


def analyze_text_with_openai(extracted_text, model_name="gpt-3.5-turbo"):
    """OpenAI APIでテキストを分析（vision不要）"""
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt_text = f"""以下のテキストを詳細に分析して、以下の情報を抽出してください：

【抽出テキスト】
{extracted_text}

【分析項目】
1. テキストの要約
2. 債券書類の種類（もし債券関連書類の場合）
3. 重要な情報（金額、日付、名称など）
4. 書類の適正性評価

分析結果を構造化された形式で提供してください。"""
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt_text
                }
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"OpenAI API ({model_name}) エラー: {str(e)}")


def calculate_accuracy(correct_text, extracted_text):
    """正解テキストと抽出テキストの適合率を計算"""
    if not correct_text or not extracted_text:
        return None
    
    # テキストを正規化（空白・改行を統一）
    correct_normalized = ' '.join(correct_text.split())
    extracted_normalized = ' '.join(extracted_text.split())
    
    # difflib.SequenceMatcherで類似度を計算
    matcher = difflib.SequenceMatcher(None, correct_normalized, extracted_normalized)
    similarity = matcher.ratio() * 100  # パーセント表示
    
    return round(similarity, 2)


def analyze_with_multiple_methods(bond_doc):
    """複数の方法で解析を実行"""
    file_path = bond_doc.uploaded_file.path
    
    # 1. OCR解析（Tesseract）
    try:
        start_time = time.time()
        if bond_doc.file_type == 'pdf':
            ocr_text = extract_text_from_pdf_ocr(file_path)
        else:
            ocr_text = extract_text_from_image_tesseract(file_path)
        
        bond_doc.ocr_result = ocr_text
        bond_doc.ocr_status = 'completed'
        bond_doc.ocr_processing_time = time.time() - start_time
    except Exception as e:
        bond_doc.ocr_status = 'failed'
        bond_doc.ocr_error = str(e)
    
    # 2. OpenAI GPT-4o解析
    try:
        start_time = time.time()
        gpt4o_text = extract_text_with_openai_vision(file_path, bond_doc.file_type, model_name="gpt-4o", instruction_prompt=bond_doc.instruction_prompt)
        bond_doc.gpt4o_result = gpt4o_text
        bond_doc.gpt4o_status = 'completed'
        bond_doc.gpt4o_processing_time = time.time() - start_time
        # 後方互換性のため、ai_resultにも保存
        bond_doc.ai_result = gpt4o_text
        bond_doc.ai_status = 'completed'
        bond_doc.ai_processing_time = time.time() - start_time
        bond_doc.ai_model_used = 'gpt-4o'
    except Exception as e:
        bond_doc.gpt4o_status = 'failed'
        bond_doc.ai_status = 'failed'
        bond_doc.ai_error = str(e)
    
    # 2-3. OpenAI gpt-4-turbo解析
    start_time = time.time()
    try:
        gpt4turbo_text = extract_text_with_openai_vision(file_path, bond_doc.file_type, model_name="gpt-4-turbo", instruction_prompt=bond_doc.instruction_prompt)
        bond_doc.gpt35_result = gpt4turbo_text
        bond_doc.gpt35_status = 'completed'
        bond_doc.gpt35_processing_time = time.time() - start_time
    except Exception as e:
        bond_doc.gpt35_status = 'failed'
        bond_doc.gpt35_result = f'GPT-4-turboエラー: {str(e)}'
        bond_doc.gpt35_processing_time = time.time() - start_time

    # 3. Gemini解析
    try:
        start_time = time.time()
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # 画像データの準備
        if bond_doc.file_type == 'pdf':
            # PDFの場合は最初のページを画像に変換
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=1)
            if images:
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='PNG')
                image_data = img_byte_arr.getvalue()
            else:
                raise Exception("PDFから画像への変換に失敗しました")
        else:
            # 画像の場合
            with open(file_path, "rb") as f:
                image_data = f.read()
        
        # Gemini 2.5 Flashモデルを使用（最新モデル）
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        # PIL Imageオブジェクトに変換
        from PIL import Image
        image = Image.open(io.BytesIO(image_data))
        
        # 指示プロンプトを使用
        prompt = bond_doc.instruction_prompt
        
        response = model.generate_content([prompt, image])
        bond_doc.gemini_result = response.text
        bond_doc.gemini_status = "completed"
        bond_doc.gemini_processing_time = time.time() - start_time
    except Exception as e:
        bond_doc.gemini_status = "failed"
        bond_doc.gemini_result = f"Geminiエラー: {str(e)}"

    # 4. Claude解析
    try:
        start_time = time.time()
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        # 画像データの準備
        if bond_doc.file_type == 'pdf':
            # PDFの場合は最初のページを画像に変換
            from pdf2image import convert_from_path
            images = convert_from_path(file_path, first_page=1, last_page=1)
            if images:
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='PNG')
                image_data = img_byte_arr.getvalue()
                media_type = "image/png"
            else:
                raise Exception("PDFから画像への変換に失敗しました")
        else:
            # 画像の場合
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            # ファイル拡張子からメディアタイプを判定
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext in ['.jpg', '.jpeg']:
                media_type = "image/jpeg"
            elif file_ext == '.png':
                media_type = "image/png"
            elif file_ext == '.gif':
                media_type = "image/gif"
            elif file_ext == '.webp':
                media_type = "image/webp"
            else:
                media_type = "image/png"  # デフォルト
        
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        # 指示プロンプトを使用
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": bond_doc.instruction_prompt
                        },
                        {
                            "type": "image",
                            "source": {"type": "base64", "media_type": media_type, "data": base64_image},
                        },
                    ],
                }
            ],
        )
        bond_doc.claude_result = message.content[0].text
        bond_doc.claude_status = "completed"
        bond_doc.claude_processing_time = time.time() - start_time
    except Exception as e:
        bond_doc.claude_status = "failed"
        bond_doc.claude_result = f"Claudeエラー: {str(e)}"

    # 5. 正解テキストがある場合は適合率を計算
    if bond_doc.correct_text:
        if bond_doc.ocr_result:
            bond_doc.ocr_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.ocr_result)
        if bond_doc.ai_result:
            bond_doc.ai_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.ai_result)
        if bond_doc.gpt4o_result:
            bond_doc.gpt4o_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.gpt4o_result)
        if bond_doc.o1_result and not bond_doc.o1_result.startswith('GPT-4-vision-previewエラー:'):
            bond_doc.o1_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.o1_result)
        if bond_doc.gpt35_result and not bond_doc.gpt35_result.startswith('GPT-4-turboエラー:'):
            bond_doc.gpt35_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.gpt35_result)
        if bond_doc.gemini_result:
            bond_doc.gemini_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.gemini_result)
        if bond_doc.claude_result:
            bond_doc.claude_accuracy = calculate_accuracy(bond_doc.correct_text, bond_doc.claude_result)
    
    # 後方互換性のため、OCR結果をextracted_textにも保存
    bond_doc.extracted_text = bond_doc.ocr_result if bond_doc.ocr_result else ""
    
    # 全体のステータスを更新
    if bond_doc.ocr_status == 'completed' or bond_doc.ai_status == 'completed':
        bond_doc.analysis_status = 'completed'
    else:
        bond_doc.analysis_status = 'failed'
        bond_doc.error_message = f"OCR: {bond_doc.ocr_error}, AI: {bond_doc.ai_error}"
    
    bond_doc.analyzed_at = timezone.now()
    bond_doc.save()


def index(request):
    """メインページ - ファイルアップロードと一覧表示"""
    if request.method == 'POST':
        form = BondDocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            bond_doc = form.save(commit=False)
            
            # ファイル名とタイプを設定
            uploaded_file = request.FILES['uploaded_file']
            bond_doc.file_name = uploaded_file.name
            
            # ファイルタイプを判定
            file_ext = os.path.splitext(uploaded_file.name)[1].lower()
            if file_ext == '.pdf':
                bond_doc.file_type = 'pdf'
            else:
                bond_doc.file_type = 'image'
            
            bond_doc.analysis_status = 'processing'
            bond_doc.save()
            
            # 複数の方法で解析を実行
            try:
                analyze_with_multiple_methods(bond_doc)
                messages.success(request, 'ファイルが正常にアップロードされ、複数の方法で解析が完了しました。')
                return redirect('bond_checker:detail', pk=bond_doc.pk)
            except Exception as e:
                bond_doc.analysis_status = 'failed'
                bond_doc.error_message = str(e)
                bond_doc.save()
                messages.error(request, f'ファイル解析中にエラーが発生しました: {str(e)}')
                return redirect('bond_checker:index')
    else:
        form = BondDocumentUploadForm()
    
    # 最新のドキュメント一覧を取得
    documents = BondDocument.objects.all()[:10]
    
    context = {
        'form': form,
        'documents': documents,
    }
    return render(request, 'bond_checker/index.html', context)


def detail(request, pk):
    """詳細ページ - 解析結果表示"""
    bond_doc = get_object_or_404(BondDocument, pk=pk)
    
    context = {
        'bond_doc': bond_doc,
        'analysis_summary': bond_doc.get_analysis_summary(),
    }
    return render(request, 'bond_checker/detail.html', context)


def document_list(request):
    """ドキュメント一覧ページ"""
    documents = BondDocument.objects.all()
    
    context = {
        'documents': documents,
    }
    return render(request, 'bond_checker/document_list.html', context)


def test_gpt4o(request):
    """GPT-4o API接続テスト"""
    from django.http import JsonResponse
    
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # シンプルなテストリクエスト
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": "Hello! Please respond with 'API connection successful!'"
                }
            ],
            max_tokens=50
        )
        
        result = {
            'status': 'success',
            'api_key_prefix': settings.OPENAI_API_KEY[:20] if settings.OPENAI_API_KEY else 'NOT_SET',
            'response': response.choices[0].message.content,
            'model': response.model
        }
        
    except Exception as e:
        result = {
            'status': 'error',
            'api_key_prefix': settings.OPENAI_API_KEY[:20] if settings.OPENAI_API_KEY else 'NOT_SET',
            'error': str(e),
            'error_type': type(e).__name__
        }
    
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False, 'indent': 2})


def clear_all(request):
    """全てのドキュメントを削除"""
    if request.method == 'POST':
        # アップロードされたファイルも削除
        for doc in BondDocument.objects.all():
            if doc.uploaded_file and os.path.exists(doc.uploaded_file.path):
                os.remove(doc.uploaded_file.path)
        
        # データベースから全て削除
        count = BondDocument.objects.count()
        BondDocument.objects.all().delete()
        
        messages.success(request, f'{count}件のドキュメントを削除しました。')
    
    return redirect('bond_checker:index')
