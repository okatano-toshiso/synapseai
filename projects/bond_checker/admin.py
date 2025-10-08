from django.contrib import admin
from .models import BondDocument


@admin.register(BondDocument)
class BondDocumentAdmin(admin.ModelAdmin):
    """債券ドキュメント管理画面"""
    
    list_display = [
        'file_name',
        'file_type',
        'analysis_status',
        'uploaded_at',
        'analyzed_at',
    ]
    list_filter = [
        'file_type',
        'analysis_status',
        'uploaded_at',
    ]
    search_fields = [
        'file_name',
        'extracted_text',
    ]
    readonly_fields = [
        'uploaded_at',
        'analyzed_at',
    ]
    fieldsets = (
        ('ファイル情報', {
            'fields': ('uploaded_file', 'file_name', 'file_type')
        }),
        ('解析結果', {
            'fields': ('analysis_status', 'extracted_text', 'error_message')
        }),
        ('タイムスタンプ', {
            'fields': ('uploaded_at', 'analyzed_at')
        }),
    )
