# backend/rag/__init__.py
"""
RAG (Retrieval Augmented Generation) লেয়ার
JSON ডাটাবেস + TXT ফাইল থেকে নলেজ রিট্রিভ করে
"""

from .searcher import KnowledgeSearcher, search_knowledge_base
from .init_rag import init_rag_system, get_knowledge_base_stats, reload_knowledge_base

__all__ = [
    'KnowledgeSearcher',
    'search_knowledge_base',
    'init_rag_system',
    'get_knowledge_base_stats',
    'reload_knowledge_base'
]