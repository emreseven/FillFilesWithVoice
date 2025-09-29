# user_manager.py - Kullanıcı Yönetim Sistemi
# Şifre korumalı kullanıcı kaydı ve giriş sistemi

import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, List, Optional

class UserManager:
    def __init__(self, users_dir: str = "users"):
        self.users_dir = users_dir
        self.users_index_file = os.path.join(users_dir, "users_index.json")
        self._ensure_users_directory()
    
    def _ensure_users_directory(self):
        """Kullanıcı dizinini ve index dosyasını oluştur"""
        if not os.path.exists(self.users_dir):
            os.makedirs(self.users_dir)
        
        if not os.path.exists(self.users_index_file):
            self._save_users_index({})
    
    def _load_users_index(self) -> Dict:
        """Kullanıcı index dosyasını yükle"""
        try:
            with open(self.users_index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_users_index(self, users_index: Dict):
        """Kullanıcı index dosyasını kaydet"""
        with open(self.users_index_file, 'w', encoding='utf-8') as f:
            json.dump(users_index, f, ensure_ascii=False, indent=2)
    
    def _generate_user_id(self) -> str:
        """Yeni kullanıcı ID'si üret"""
        return str(uuid.uuid4()).replace('-', '')[:8]
    
    def _hash_password(self, password: str) -> str:
        """Şifreyi hash'le"""
        # Basit SHA-256 hash (gerçek uygulamada bcrypt kullanılmalı)
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Şifreyi doğrula"""
        return self._hash_password(password) == hashed
    
    def _get_user_file_path(self, user_id: str) -> str:
        """Kullanıcı dosya yolunu al"""
        return os.path.join(self.users_dir, f"user_{user_id}.json")
    
    def register_user(self, username: str, email: str, role: str, password: str, security_question: str = None, security_answer: str = None) -> Optional[Dict]:
        """Yeni kullanıcı kaydet"""
        # Kullanıcı adı kontrolü
        if self.get_user_by_username(username):
            return None  # Kullanıcı adı zaten var
        
        # Yeni kullanıcı oluştur
        user_id = self._generate_user_id()
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "display_name": username,  # Kullanıcı adını görünen ad olarak kullan
            "role": role,
            "password_hash": self._hash_password(password),
            "status": "pending",  # pending, approved, rejected
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "approved_by": None,
            "approved_at": None
        }
        
        # Güvenlik sorusu ve cevabını ekle
        if security_question and security_answer:
            user_data["security_question"] = security_question
            user_data["security_answer"] = security_answer.lower().strip()
        
        # Kullanıcı dosyasını kaydet
        user_file = self._get_user_file_path(user_id)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        
        # Index'i güncelle
        users_index = self._load_users_index()
        users_index[username] = {
            "user_id": user_id,
            "display_name": username,
            "email": email,
            "role": role,
            "status": "pending",
            "created_at": user_data["created_at"]
        }
        self._save_users_index(users_index)
        
        return user_data
    
    def authenticate_user(self, username: str, password: str) -> tuple[Optional[Dict], str]:
        """Kullanıcı adı ve şifre ile giriş doğrulama"""
        user = self.get_user_by_username(username)
        if not user:
            return None, "Kullanıcı bulunamadı"
        
        # Onay durumu kontrolü
        if user.get("status") == "pending":
            return None, "Hesabınız henüz admin tarafından onaylanmamış"
        elif user.get("status") == "rejected":
            return None, "Hesabınız reddedilmiş"
        elif user.get("status") != "approved":
            return None, "Hesap durumu geçersiz"
        
        # Şifre doğrulama
        if self._verify_password(password, user.get("password_hash", "")):
            return user, "success"
        return None, "Şifre hatalı"
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Kullanıcı adına göre kullanıcı bilgilerini al"""
        users_index = self._load_users_index()
        
        if username not in users_index:
            return None
        
        user_info = users_index[username]
        user_id = user_info["user_id"]
        
        # Tam kullanıcı verilerini yükle
        return self.get_user_by_id(user_id)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Kullanıcı ID'sine göre kullanıcı bilgilerini al"""
        user_file = self._get_user_file_path(user_id)
        
        if not os.path.exists(user_file):
            return None
        
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def update_last_login(self, user_id: str):
        """Son giriş zamanını güncelle"""
        user_data = self.get_user_by_id(user_id)
        if user_data:
            user_data["last_login"] = datetime.now().isoformat()
            user_file = self._get_user_file_path(user_id)
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, ensure_ascii=False, indent=2)
    
    def get_all_users(self) -> List[Dict]:
        """Tüm kullanıcıları listele"""
        users_index = self._load_users_index()
        users = []
        
        for username, user_info in users_index.items():
            user_data = self.get_user_by_id(user_info["user_id"])
            if user_data:
                users.append(user_data)
        
        return users
    
    def get_user_permissions(self, role: str) -> Dict:
        """Rol bazlı izinleri al"""
        ROLE_PERMISSIONS = {
            "admin": {
                "can_delete_sessions": True,
                "available_forms": [
                    "Ek 1-2-3",
                    "Ek 4", 
                    "Ek 6", 
                    "Ek 8", 
                    "Ek 9", 
                    "Ek 11", 
                    "Ek 15"
                ]
            },
            "level1": {
                "can_delete_sessions": False,
                "available_forms": ["Ek 1-2-3"]
            },
            "level2": {
                "can_delete_sessions": False,
                "available_forms": ["Ek 4", "Ek 6", "Ek 8", "Ek 9", "Ek 11", "Ek 15"]
            }
        }
        
        return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["level1"])
    
    def get_pending_users(self) -> List[Dict]:
        """Onay bekleyen kullanıcıları getir"""
        users = self.get_all_users()
        return [user for user in users if user.get("status") == "pending"]
    
    def approve_user(self, user_id: str, admin_user_id: str) -> bool:
        """Kullanıcıyı onayla"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Kullanıcı durumunu güncelle
        user["status"] = "approved"
        user["approved_by"] = admin_user_id
        user["approved_at"] = datetime.now().isoformat()
        
        # Dosyayı kaydet
        user_file = self._get_user_file_path(user_id)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=2)
        
        # Index'i güncelle
        users_index = self._load_users_index()
        if user["username"] in users_index:
            users_index[user["username"]]["status"] = "approved"
            self._save_users_index(users_index)
        
        return True
    
    def reject_user(self, user_id: str, admin_user_id: str) -> bool:
        """Kullanıcıyı reddet ve sistemden sil"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Kullanıcı dosyasını sil
        user_file = self._get_user_file_path(user_id)
        try:
            if os.path.exists(user_file):
                os.remove(user_file)
        except Exception:
            pass
        
        # Index'den çıkar
        users_index = self._load_users_index()
        if user["username"] in users_index:
            del users_index[user["username"]]
            self._save_users_index(users_index)
        
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcıyı tamamen sil (admin hariç)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Admin kullanıcısını silemez
        if user.get("username") == "admin":
            return False
        
        # Kullanıcı dosyasını sil
        user_file = self._get_user_file_path(user_id)
        try:
            if os.path.exists(user_file):
                os.remove(user_file)
        except Exception:
            return False
        
        # Index'den çıkar
        users_index = self._load_users_index()
        if user["username"] in users_index:
            del users_index[user["username"]]
            self._save_users_index(users_index)
        
        return True
    
    def change_user_role(self, user_id: str, new_role: str, admin_user_id: str) -> bool:
        """Kullanıcının rolünü değiştir (admin hariç)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        # Admin kullanıcısının rolü değiştirilemez
        if user.get("username") == "admin":
            return False
        
        # Geçerli rol kontrolü
        valid_roles = ["admin", "level1", "level2"]
        if new_role not in valid_roles:
            return False
        
        # Kullanıcı verisini güncelle
        user["role"] = new_role
        user["role_changed_by"] = admin_user_id
        user["role_changed_at"] = datetime.now().isoformat()
        
        # Dosyayı kaydet
        user_file = self._get_user_file_path(user_id)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump(user, f, ensure_ascii=False, indent=2)
        
        # Index'i güncelle
        users_index = self._load_users_index()
        if user["username"] in users_index:
            users_index[user["username"]]["role"] = new_role
            self._save_users_index(users_index)
        
        return True
    
    def get_security_question(self, username: str) -> Optional[str]:
        """Kullanıcının güvenlik sorusunu al"""
        try:
            user = self.get_user_by_username(username)
            if user and 'security_question' in user:
                return user['security_question']
            return None
        except Exception as e:
            print(f"Error getting security question: {e}")
            return None

    def verify_security_answer(self, username: str, answer: str) -> bool:
        """Güvenlik sorusu cevabını doğrula"""
        try:
            user = self.get_user_by_username(username)
            if user and 'security_answer' in user:
                # Büyük/küçük harf duyarsız karşılaştırma
                stored_answer = user['security_answer'].lower().strip()
                provided_answer = answer.lower().strip()
                return stored_answer == provided_answer
            return False
        except Exception as e:
            print(f"Error verifying security answer: {e}")
            return False

    def reset_password(self, username: str, new_password: str) -> tuple[bool, str]:
        """Güvenlik sorusu doğrulandıktan sonra şifreyi sıfırla"""
        try:
            user = self.get_user_by_username(username)
            if not user:
                return False, "Kullanıcı bulunamadı!"
            
            # Şifreyi güncelle
            user['password_hash'] = self._hash_password(new_password)
            
            # Kullanıcı dosyasını güncelle
            user_file = self._get_user_file_path(user['user_id'])
            with open(user_file, 'w', encoding='utf-8') as f:
                json.dump(user, f, ensure_ascii=False, indent=2)
            
            return True, "Şifre başarıyla sıfırlandı!"
        
        except Exception as e:
            return False, f"Şifre sıfırlanırken hata: {str(e)}"
    
    def create_initial_admin_if_needed(self) -> bool:
        """Eğer hiç kullanıcı yoksa ilk admin kullanıcısını oluştur"""
        users = self.get_all_users()
        if not users:
            # İlk admin kullanıcısını oluştur
            admin_data = {
                "user_id": self._generate_user_id(),
                "username": "admin",
                "email": "admin@system.local",
                "display_name": "admin",
                "role": "admin",
                "password_hash": self._hash_password("admin123"),
                "status": "approved",  # İlk admin otomatik onaylanır
                "created_at": datetime.now().isoformat(),
                "last_login": None,
                "approved_by": "system",
                "approved_at": datetime.now().isoformat()
            }
            
            # Admin dosyasını kaydet
            admin_file = self._get_user_file_path(admin_data["user_id"])
            with open(admin_file, 'w', encoding='utf-8') as f:
                json.dump(admin_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            users_index = self._load_users_index()
            users_index["admin"] = {
                "user_id": admin_data["user_id"],
                "display_name": "admin",
                "email": "admin@system.local",
                "role": "admin",
                "status": "approved",
                "created_at": admin_data["created_at"]
            }
            self._save_users_index(users_index)
            
            return True
        return False

# Global user manager instance
_user_manager = None

def get_user_manager() -> UserManager:
    """Global user manager instance'ını al"""
    global _user_manager
    if _user_manager is None:
        _user_manager = UserManager()
    return _user_manager
