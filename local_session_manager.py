"""
Local dosya tabanlı session yönetimi modülü
JSON dosyaları ile session verilerini saklar
"""
import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st


class LocalSessionManager:
    def __init__(self, sessions_dir: str = "sessions"):
        self.sessions_dir = sessions_dir
        self.sessions_file = os.path.join(sessions_dir, "sessions_index.json")
        self._ensure_directory()
        
    def _ensure_directory(self):
        """Sessions klasörünü oluştur"""
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
            
    def _load_sessions_index(self) -> Dict[str, Any]:
        """Sessions index dosyasını yükle"""
        if not os.path.exists(self.sessions_file):
            return {}
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"Sessions index okunamadı: {e}")
            return {}
    
    def _save_sessions_index(self, sessions_index: Dict[str, Any]):
        """Sessions index dosyasını kaydet"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Sessions index kaydedilemedi: {e}")
    
    def _get_session_file_path(self, session_id: str) -> str:
        """Session dosya yolunu al"""
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def create_session(self, session_name: str, user_info: Optional[Dict] = None) -> str:
        """Yeni session oluştur"""
        try:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"
            now = datetime.now().isoformat()
            
            # Session verisi
            session_data = {
                "session_id": session_id,
                "session_name": session_name,
                "extracted_data": {},
                "transcript": "",  # Transcript verisi için alan
                "created_date": now,
                "last_modified": now,
                "voice_count": 0
            }
            
            # Kullanıcı bilgilerini ekle
            if user_info:
                session_data.update({
                    "created_by": user_info.get("user_id"),
                    "creator_name": user_info.get("display_name"),
                    "creator_role": user_info.get("role")
                })
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            sessions_index[session_id] = {
                "session_name": session_name,
                "created_date": now,
                "last_modified": now,
                "file_path": session_file
            }
            self._save_sessions_index(sessions_index)
            
            return session_id
            
        except Exception as e:
            st.error(f"Session oluşturma başarısız: {e}")
            return ""
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Tüm session'ları getir"""
        sessions = []
        sessions_index = self._load_sessions_index()
        
        for session_id, index_data in sessions_index.items():
            try:
                session_file = self._get_session_file_path(session_id)
                if os.path.exists(session_file):
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    sessions.append(session_data)
                else:
                    # Dosya yoksa index'ten kaldır
                    st.warning(f"Session dosyası bulunamadı: {session_id}")
                    
            except Exception as e:
                st.warning(f"Session okunamadı ({session_id}): {e}")
                continue
        
        # Son değişiklik tarihine göre sırala (en yeni önce)
        sessions.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
        return sessions
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Belirli bir session'ı getir"""
        try:
            session_file = self._get_session_file_path(session_id)
            if not os.path.exists(session_file):
                return None
                
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            st.error(f"Session okunamadı: {e}")
            return None
    
    def update_session_data(self, session_id: str, new_data: Dict[str, str], merge: bool = True) -> bool:
        """Session verisini güncelle"""
        try:
            # Mevcut session'ı al
            session_data = self.get_session(session_id)
            if not session_data:
                st.error(f"Session bulunamadı: {session_id}")
                return False
            
            # Veriyi birleştir veya değiştir
            if merge:
                current_extracted = session_data.get('extracted_data', {})
                merged_data = {**current_extracted, **new_data}
                session_data['extracted_data'] = merged_data
            else:
                session_data['extracted_data'] = new_data
            
            # Voice count'u artır (sadece merge durumunda)
            if merge and new_data:
                session_data['voice_count'] = session_data.get('voice_count', 0) + 1
            
            # Son değişiklik tarihini güncelle
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            if session_id in sessions_index:
                sessions_index[session_id]['last_modified'] = session_data['last_modified']
                self._save_sessions_index(sessions_index)
            
            return True
            
        except Exception as e:
            st.error(f"Session güncelleme başarısız: {e}")
            return False
    
    def update_session_transcript(self, session_id: str, transcript: str) -> bool:
        """Session transcript verilerini güncelle"""
        try:
            # Mevcut session'ı al
            session_data = self.get_session(session_id)
            if not session_data:
                st.error(f"Session bulunamadı: {session_id}")
                return False
            
            # Transcript'i güncelle
            session_data['transcript'] = transcript
            
            # Son değişiklik tarihini güncelle
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            if session_id in sessions_index:
                sessions_index[session_id]['last_modified'] = session_data['last_modified']
                self._save_sessions_index(sessions_index)
            
            return True
            
        except Exception as e:
            st.error(f"Transcript güncelleme başarısız: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """Session'ı sil"""
        try:
            # Session dosyasını sil
            session_file = self._get_session_file_path(session_id)
            if os.path.exists(session_file):
                os.remove(session_file)
            
            # Index'ten kaldır
            sessions_index = self._load_sessions_index()
            if session_id in sessions_index:
                del sessions_index[session_id]
                self._save_sessions_index(sessions_index)
            
            return True
            
        except Exception as e:
            st.error(f"Session silme başarısız: {e}")
            return False
    
    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Session adını değiştir"""
        try:
            # Session verisini güncelle
            session_data = self.get_session(session_id)
            if not session_data:
                return False
            
            session_data['session_name'] = new_name
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            if session_id in sessions_index:
                sessions_index[session_id]['session_name'] = new_name
                sessions_index[session_id]['last_modified'] = session_data['last_modified']
                self._save_sessions_index(sessions_index)
            
            return True
            
        except Exception as e:
            st.error(f"Session yeniden adlandırma başarısız: {e}")
            return False
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Session verisini kaydet (unified_app.py uyumluluğu için)"""
        try:
            session_data['last_modified'] = datetime.now().isoformat()
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            if session_id in sessions_index:
                sessions_index[session_id]['session_name'] = session_data.get('session_name', 'Unknown')
                sessions_index[session_id]['last_modified'] = session_data['last_modified']
                self._save_sessions_index(sessions_index)
            
            return True
            
        except Exception as e:
            st.error(f"Session kaydetme başarısız: {e}")
            return False
    
    def update_session_name(self, session_id: str, new_name: str) -> bool:
        """Session ismini güncelle (unified_app.py uyumluluğu için)"""
        return self.rename_session(session_id, new_name)
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Session'ı export için hazırla"""
        return self.get_session(session_id)
    
    def import_session(self, session_data: Dict[str, Any], new_name: Optional[str] = None) -> str:
        """Session'ı import et"""
        try:
            # Yeni session ID oluştur
            new_session_id = f"sess_{uuid.uuid4().hex[:8]}"
            now = datetime.now().isoformat()
            
            # Session verisini hazırla
            imported_data = {
                "session_id": new_session_id,
                "session_name": new_name or f"Imported - {session_data.get('session_name', 'Unknown')}",
                "extracted_data": session_data.get('extracted_data', {}),
                "created_date": now,
                "last_modified": now,
                "voice_count": session_data.get('voice_count', 0),
                "original_created_date": session_data.get('created_date'),
                "import_date": now
            }
            
            # Session dosyasını kaydet
            session_file = self._get_session_file_path(new_session_id)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(imported_data, f, ensure_ascii=False, indent=2)
            
            # Index'i güncelle
            sessions_index = self._load_sessions_index()
            sessions_index[new_session_id] = {
                "session_name": imported_data['session_name'],
                "created_date": now,
                "last_modified": now,
                "file_path": session_file
            }
            self._save_sessions_index(sessions_index)
            
            return new_session_id
            
        except Exception as e:
            st.error(f"Session import başarısız: {e}")
            return ""


# Global local session manager instance
local_session_manager = LocalSessionManager()


def get_local_session_manager() -> LocalSessionManager:
    """Global local session manager instance'ını getir"""
    return local_session_manager


def merge_extracted_data(existing_data: Dict[str, str], new_data: Dict[str, str]) -> Dict[str, str]:
    """
    İki veri setini akıllıca birleştir
    Çakışma durumunda yeni veriyi tercih et
    """
    merged = existing_data.copy()
    
    for key, value in new_data.items():
        if value and str(value).strip():  # Sadece boş olmayan değerleri ekle
            merged[key] = value
    
    return merged


def detect_conflicts(existing_data: Dict[str, str], new_data: Dict[str, str]) -> List[str]:
    """
    Çakışan placeholder'ları tespit et
    """
    conflicts = []
    
    for key, new_value in new_data.items():
        if key in existing_data and existing_data[key] and new_value:
            if existing_data[key] != new_value:
                conflicts.append(key)
    
    return conflicts

