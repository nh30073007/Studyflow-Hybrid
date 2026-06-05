# backend/database/security.py
"""
ডাটাবেস সিকিউরিটি
- pg_tde ট্রান্সপারেন্ট ডাটা এনক্রিপশন
- Row Level Security (RLS)
- ডাটা এনক্রিপশন ফাংশন
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine
import os
from typing import Optional
import hashlib
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

# এনক্রিপশন কী জেনারেট বা লোড
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # নতুন কী জেনারেট
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️ নতুন এনক্রিপশন কী জেনারেট হয়েছে! .env ফাইলে সেভ করুন:")
    print(f"ENCRYPTION_KEY={ENCRYPTION_KEY}")
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY

# Fernet সাইফার
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    """ডাটা এনক্রিপ্ট করে"""
    if not data:
        return data
    if isinstance(data, str):
        return cipher.encrypt(data.encode()).decode()
    return cipher.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    """এনক্রিপ্টেড ডাটা ডিক্রিপ্ট করে"""
    if not encrypted_data:
        return encrypted_data
    try:
        return cipher.decrypt(encrypted_data.encode()).decode()
    except:
        return encrypted_data

class SecurityManager:
    """সিকিউরিটি ম্যানেজার"""
    
    @staticmethod
    def encrypt_sensitive_fields(data: dict, fields: list) -> dict:
        """সেনসিটিভ ফিল্ড এনক্রিপ্ট করে"""
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = encrypt_data(str(encrypted[field]))
        return encrypted
    
    @staticmethod
    def decrypt_sensitive_fields(data: dict, fields: list) -> dict:
        """এনক্রিপ্টেড ফিল্ড ডিক্রিপ্ট করে"""
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = decrypt_data(decrypted[field])
                except:
                    pass
        return decrypted

def setup_pg_tde(engine):
    """
    PostgreSQL pg_tde এক্সটেনশন সেটআপ
    যদি PostgreSQL না থাকে, তাহলে শুধু প্রিন্ট করবে
    """
    try:
        # চেক করো PostgreSQL ব্যবহার করছে কিনা
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_tde;"))
                conn.commit()
                print("✅ pg_tde এনক্রিপশন সেটআপ হয়েছে!")
        else:
            print("ℹ️ SQLite ব্যবহার করা হচ্ছে - pg_tde স্কিপ করা হয়েছে")
    except Exception as e:
        print(f"⚠️ pg_tde সেটআপ স্কিপ করা হয়েছে (PostgreSQL প্রয়োজন): {e}")

def enable_row_level_security(engine, table_name: str):
    """টেবিলে Row Level Security ইমপ্লিমেন্ট করে"""
    try:
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))
                conn.commit()
                print(f"✅ RLS ইমপ্লিমেন্ট হয়েছে: {table_name}")
    except Exception as e:
        print(f"⚠️ RLS সেটআপ স্কিপ করা হয়েছে: {e}")

def create_rls_policies(engine):
    """RLS পলিসি তৈরি করে"""
    try:
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                # শিশু পলিসি
                conn.execute(text("""
                    CREATE POLICY IF NOT EXISTS child_select_policy ON child_progress
                    FOR SELECT USING (user_id = current_setting('app.current_user_id', true));
                """))
                conn.commit()
                print("✅ RLS পলিসি তৈরি হয়েছে!")
    except Exception as e:
        print(f"⚠️ RLS পলিসি তৈরি স্কিপ করা হয়েছে: {e}")

def set_current_user(session, user_id: str, role: str = "child"):
    """বর্তমান ইউজার সেট করে (RLS এর জন্য)"""# backend/database/security.py
"""
ডাটাবেস সিকিউরিটি - সিম্পল ভার্সন (এনক্রিপশন ছাড়া)
দ্রুত রান করার জন্য - পরে এনক্রিপশন যোগ করা যাবে
"""

from sqlalchemy import text
from sqlalchemy.engine import Engine
import os
from typing import Optional

def encrypt_data(data: str) -> str:
    """ডাটা এনক্রিপ্ট করে - বর্তমানে কোন এনক্রিপশন নেই"""
    return data if data else data

def decrypt_data(encrypted_data: str) -> str:
    """এনক্রিপ্টেড ডাটা ডিক্রিপ্ট করে - বর্তমানে কোন ডিক্রিপশন নেই"""
    return encrypted_data if encrypted_data else encrypted_data

class SecurityManager:
    """সিকিউরিটি ম্যানেজার - সিম্পল মোড"""
    
    @staticmethod
    def encrypt_sensitive_fields(data: dict, fields: list) -> dict:
        """সেনসিটিভ ফিল্ড এনক্রিপ্ট করে - বর্তমানে কোন পরিবর্তন নেই"""
        return data
    
    @staticmethod
    def decrypt_sensitive_fields(data: dict, fields: list) -> dict:
        """এনক্রিপ্টেড ফিল্ড ডিক্রিপ্ট করে - বর্তমানে কোন পরিবর্তন নেই"""
        return data

def setup_pg_tde(engine):
    """
    PostgreSQL pg_tde এক্সটেনশন সেটআপ
    বর্তমানে স্কিপ করা হচ্ছে
    """
    print("ℹ️ pg_tde সেটআপ স্কিপ করা হয়েছে (সিম্পল মোড)")

def enable_row_level_security(engine, table_name: str):
    """টেবিলে Row Level Security - বর্তমানে স্কিপ"""
    pass

def create_rls_policies(engine):
    """RLS পলিসি - বর্তমানে স্কিপ"""
    pass

def set_current_user(session, user_id: str, role: str = "child"):
    """বর্তমান ইউজার সেট করে - বর্তমানে স্কিপ"""
    pass

def get_connection_params() -> dict:
    """ডাটাবেস কানেকশন প্যারামিটার"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "studyflow_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
    }
    try:
        session.execute(text(f"SET app.current_user_id = '{user_id}'"))
        session.execute(text(f"SET app.current_user_role = '{role}'"))
    except:
        pass  # SQLite তে এটা কাজ করবে না

def get_connection_params() -> dict:
    """ডাটাবেস কানেকশন প্যারামিটার রিটার্ন করে"""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "studyflow_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "encryption_key": ENCRYPTION_KEY
    }