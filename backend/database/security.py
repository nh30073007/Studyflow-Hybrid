from sqlalchemy import text
from sqlalchemy.engine import Engine
import os
from typing import Optional
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"⚠️ নতুন এনক্রিপশন কী জেনারেট হয়েছে! .env ফাইলে সেভ করুন:")
    print(f"ENCRYPTION_KEY={ENCRYPTION_KEY}")
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY

cipher = Fernet(ENCRYPTION_KEY)

def encrypt_data(data: str) -> str:
    if not data:
        return data
    if isinstance(data, str):
        return cipher.encrypt(data.encode()).decode()
    return cipher.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return encrypted_data
    try:
        return cipher.decrypt(encrypted_data.encode()).decode()
    except:
        return encrypted_data

class SecurityManager:
    
    @staticmethod
    def encrypt_sensitive_fields(data: dict, fields: list) -> dict:
        encrypted = data.copy()
        for field in fields:
            if field in encrypted and encrypted[field]:
                encrypted[field] = encrypt_data(str(encrypted[field]))
        return encrypted
    
    @staticmethod
    def decrypt_sensitive_fields(data: dict, fields: list) -> dict:
        decrypted = data.copy()
        for field in fields:
            if field in decrypted and decrypted[field]:
                try:
                    decrypted[field] = decrypt_data(decrypted[field])
                except:
                    pass
        return decrypted

def setup_pg_tde(engine):
    try:
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
    try:
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"))
                conn.commit()
                print(f"✅ RLS ইমপ্লিমেন্ট হয়েছে: {table_name}")
    except Exception as e:
        print(f"⚠️ RLS সেটআপ স্কিপ করা হয়েছে: {e}")

def create_rls_policies(engine):
    try:
        if "postgresql" in str(engine.url):
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE POLICY IF NOT EXISTS child_select_policy ON child_progress
                    FOR SELECT USING (user_id = current_setting('app.current_user_id', true));
                """))
                conn.commit()
                print("✅ RLS পলিসি তৈরি হয়েছে!")
    except Exception as e:
        print(f"⚠️ RLS পলিসি তৈরি স্কিপ করা হয়েছে: {e}")

def set_current_user(session, user_id: str, role: str = "child"):
    try:
        session.execute(text(f"SET app.current_user_id = '{user_id}'"))
        session.execute(text(f"SET app.current_user_role = '{role}'"))
    except:
        pass

def get_connection_params() -> dict:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "studyflow_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "encryption_key": ENCRYPTION_KEY
    }
