import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class FeedbackManager:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.root = os.path.join(base_dir, "feedbacks")
        self.index_path = os.path.join(self.root, "feedbacks_index.json")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        os.makedirs(self.root, exist_ok=True)
        if not os.path.exists(self.index_path):
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump({"feedback_ids": []}, f, ensure_ascii=False, indent=2)

    def _load_index(self) -> List[str]:
        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f) or {}
                return list(data.get("feedback_ids", []))
        except Exception:
            return []

    def _save_index(self, ids: List[str]) -> bool:
        try:
            with open(self.index_path, "w", encoding="utf-8") as f:
                json.dump({"feedback_ids": ids}, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def _feedback_path(self, feedback_id: str) -> str:
        return os.path.join(self.root, f"feedback_{feedback_id}.json")

    def submit_feedback(self, user: Dict, message: str) -> Optional[str]:
        try:
            feedback_id = uuid.uuid4().hex[:12]
            now_iso = datetime.utcnow().isoformat()
            payload = {
                "feedback_id": feedback_id,
                "created_at": now_iso,
                "status": "pending",
                "message": message.strip(),
                "submitted_by": {
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "display_name": user.get("display_name"),
                    "role": user.get("role"),
                },
                # Varsayılan: sistemde tek bir en üst admin var → username == "admin"
                "assigned_to": "admin",
            }

            with open(self._feedback_path(feedback_id), "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            ids = self._load_index()
            ids.insert(0, feedback_id)
            self._save_index(ids)
            return feedback_id
        except Exception:
            return None

    def get_all_feedbacks(self) -> List[Dict]:
        ids = self._load_index()
        out: List[Dict] = []
        for fid in ids:
            try:
                with open(self._feedback_path(fid), "r", encoding="utf-8") as f:
                    out.append(json.load(f))
            except Exception:
                continue
        # created_at'e göre en yeni üste
        out.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return out

    def get_pending_count(self) -> int:
        return sum(1 for fb in self.get_all_feedbacks() if fb.get("status") == "pending")

    def set_status(self, feedback_id: str, status: str) -> bool:
        try:
            path = self._feedback_path(feedback_id)
            if not os.path.exists(path):
                return False
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["status"] = status
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def delete_feedback(self, feedback_id: str) -> bool:
        try:
            path = self._feedback_path(feedback_id)
            if os.path.exists(path):
                os.remove(path)
            ids = [x for x in self._load_index() if x != feedback_id]
            return self._save_index(ids)
        except Exception:
            return False


_singleton: Optional[FeedbackManager] = None


def get_feedback_manager() -> FeedbackManager:
    global _singleton
    if _singleton is None:
        base_dir = os.getcwd()
        _singleton = FeedbackManager(base_dir)
    return _singleton


