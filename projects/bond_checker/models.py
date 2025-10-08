from django.db import models
from django.utils import timezone
import json


class BondDocument(models.Model):
    """債券ドキュメントモデル"""
    
    # ファイル情報
    uploaded_file = models.FileField(
        upload_to='bond_documents/%Y/%m/%d/',
        verbose_name='アップロードファイル'
    )
    file_name = models.CharField(max_length=255, verbose_name='ファイル名')
    file_type = models.CharField(
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('image', '画像'),
        ],
        verbose_name='ファイルタイプ'
    )
    
    # 解析結果（後方互換性のため残す）
    extracted_text = models.TextField(blank=True, null=True, verbose_name='抽出テキスト')
    analysis_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', '処理待ち'),
            ('processing', '処理中'),
            ('completed', '完了'),
            ('failed', '失敗'),
        ],
        default='pending',
        verbose_name='解析ステータス'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='エラーメッセージ')
    
    # OCR解析結果（Tesseract）
    ocr_result = models.TextField(blank=True, null=True, verbose_name='OCR解析結果')
    ocr_status = models.CharField(max_length=20, default='pending', verbose_name='OCRステータス')
    ocr_processing_time = models.FloatField(null=True, blank=True, verbose_name='OCR処理時間(秒)')
    ocr_error = models.TextField(blank=True, null=True, verbose_name='OCRエラー')
    
    # 画像認識結果（Vision API）
    vision_result = models.TextField(blank=True, null=True, verbose_name='Vision API結果')
    vision_status = models.CharField(max_length=20, default='pending', verbose_name='Visionステータス')
    vision_processing_time = models.FloatField(null=True, blank=True, verbose_name='Vision処理時間(秒)')
    vision_error = models.TextField(blank=True, null=True, verbose_name='Visionエラー')
    
    # 生成AI解析結果（GPT/Claude）
    ai_result = models.TextField(blank=True, null=True, verbose_name='生成AI解析結果')
    ai_status = models.CharField(max_length=20, default='pending', verbose_name='AIステータス')
    ai_processing_time = models.FloatField(null=True, blank=True, verbose_name='AI処理時間(秒)')
    ai_error = models.TextField(blank=True, null=True, verbose_name='AIエラー')
    ai_model_used = models.CharField(max_length=50, blank=True, null=True, verbose_name='使用AIモデル')
    
    # 債券書類分類結果
    document_category = models.CharField(max_length=100, blank=True, null=True, verbose_name='書類カテゴリー')
    is_valid = models.BooleanField(null=True, blank=True, verbose_name='書類の適正性')
    validation_notes = models.TextField(blank=True, null=True, verbose_name='検証メモ')
    
    # 正解テキストと適合率
    correct_text = models.TextField(blank=True, null=True, verbose_name='正解テキスト')
    ocr_accuracy = models.FloatField(null=True, blank=True, verbose_name='OCR適合率(%)')
    ai_accuracy = models.FloatField(null=True, blank=True, verbose_name='AI適合率(%)')

    # Gemini解析結果
    gemini_result = models.TextField(blank=True, null=True, verbose_name='Gemini解析結果')
    gemini_status = models.CharField(max_length=20, default='pending', verbose_name='Geminiステータス')
    gemini_processing_time = models.FloatField(null=True, blank=True, verbose_name='Gemini処理時間(秒)')
    gemini_accuracy = models.FloatField(null=True, blank=True, verbose_name='Gemini適合率(%)')

    # Claude解析結果
    claude_result = models.TextField(blank=True, null=True, verbose_name='Claude解析結果')
    claude_status = models.CharField(max_length=20, default='pending', verbose_name='Claudeステータス')
    claude_processing_time = models.FloatField(null=True, blank=True, verbose_name='Claude処理時間(秒)')
    claude_accuracy = models.FloatField(null=True, blank=True, verbose_name='Claude適合率(%)')
    
    # タイムスタンプ
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name='アップロード日時')
    analyzed_at = models.DateTimeField(blank=True, null=True, verbose_name='解析完了日時')
    
    class Meta:
        verbose_name = '債券ドキュメント'
        verbose_name_plural = '債券ドキュメント'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
    
    def get_analysis_summary(self):
        """解析サマリーを取得"""
        return {
            'ocr': {
                'status': self.ocr_status,
                'time': self.ocr_processing_time,
                'result_length': len(self.ocr_result) if self.ocr_result else 0
            },
            'vision': {
                'status': self.vision_status,
                'time': self.vision_processing_time,
                'result_length': len(self.vision_result) if self.vision_result else 0
            },
            'ai': {
                'status': self.ai_status,
                'time': self.ai_processing_time,
                'result_length': len(self.ai_result) if self.ai_result else 0,
                'model': self.ai_model_used
            }
        }
