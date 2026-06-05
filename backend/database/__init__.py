# backend/database/__init__.py
"""
StudyFlow AI - ডাটাবেস লেয়ার
PostgreSQL + SQLite সাপোর্ট
"""

from .db import (
    get_db,
    init_db,
    get_session,
    SessionLocal,
    engine,
    close_db,
    test_connection
)
from .models import (
    Base,
    User,
    ChildProgress,
    ChatHistory,
    TopicMastery,
    Reminder
)
from .security import (
    setup_pg_tde,
    enable_row_level_security,
    create_rls_policies,
    encrypt_data,
    decrypt_data,
    SecurityManager
)
from .crud import (
    create_user,
    get_user,
    update_user,
    update_child_progress,
    get_child_progress,
    save_chat_history,
    get_chat_history,
    create_reminder,
    get_pending_reminders,
    get_child_report,
    get_all_children,
    get_all_users,
    get_user_stats,
    get_top_performers,
    get_topic_recommendations,
    get_dashboard_stats
)

__all__ = [
    # DB
    'get_db',
    'init_db',
    'get_session',
    'SessionLocal',
    'engine',
    'close_db',
    'test_connection',
    
    # Models
    'Base',
    'User',
    'ChildProgress',
    'ChatHistory',
    'TopicMastery',
    'Reminder',
    
    # Security
    'setup_pg_tde',
    'enable_row_level_security',
    'create_rls_policies',
    'encrypt_data',
    'decrypt_data',
    'SecurityManager',
    
    # CRUD
    'create_user',
    'get_user',
    'update_user',
    'update_child_progress',
    'get_child_progress',
    'save_chat_history',
    'get_chat_history',
    'create_reminder',
    'get_pending_reminders',
    'get_child_report',
    'get_all_children',
    'get_all_users',
    'get_user_stats',
    'get_top_performers',
    'get_topic_recommendations',
    'get_dashboard_stats'
]