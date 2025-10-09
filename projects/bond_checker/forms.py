from django import forms
from .models import BondDocument


class BondDocumentUploadForm(forms.ModelForm):
    """債券ドキュメントアップロードフォーム"""
    
    class Meta:
        model = BondDocument
        fields = ['uploaded_file', 'instruction_prompt', 'correct_text']
        widgets = {
            'uploaded_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.gif',
            }),
            'instruction_prompt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'LLMに送信する指示プロンプトを入力してください',
            }),
            'correct_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': '正解テキストを入力してください（任意）\n※ 入力すると適合率が自動計算されます',
            })
        }
        labels = {
            'uploaded_file': 'PDFまたは画像ファイルを選択',
            'instruction_prompt': '指示プロンプト',
            'correct_text': '正解テキスト（任意）',
        }
    
    def clean_uploaded_file(self):
        """ファイルのバリデーション"""
        uploaded_file = self.cleaned_data.get('uploaded_file')
        
        if uploaded_file:
            # ファイルサイズチェック（10MB以下）
            if uploaded_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('ファイルサイズは10MB以下にしてください。')
            
            # ファイル拡張子チェック
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif']
            file_name = uploaded_file.name.lower()
            
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    'PDF、JPG、PNG、GIFファイルのみアップロード可能です。'
                )
        
        return uploaded_file
