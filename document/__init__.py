"""
Document Domain — InputFile → Document.

负责：
- Document Dispatcher（路由到对应 Parser）
- Parser（将 InputFile 解析为结构化 Document）
- Document Model
- Document Service（文档生命周期管理）
"""
