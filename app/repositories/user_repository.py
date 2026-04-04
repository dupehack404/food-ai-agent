import json
from pathlib import Path
from typing import Optional

from app.models.user_profile import UserProfile


class UserRepository:
    def __init__(self, file_path: str = "data/users.json"):
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file()
        self._storage: dict[str, UserProfile] = self._load_storage()

    def _ensure_file(self) -> None:
        if not self.file_path.exists():
            self.file_path.write_text("{}", encoding="utf-8")

    def _load_storage(self) -> dict[str, UserProfile]:
        raw_data = json.loads(self.file_path.read_text(encoding="utf-8"))
        return {
            user_id: UserProfile.model_validate(profile_data)
            for user_id, profile_data in raw_data.items()
        }

    def _persist(self) -> None:
        raw_data = {
            user_id: profile.model_dump()
            for user_id, profile in self._storage.items()
        }
        self.file_path.write_text(
            json.dumps(raw_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        return self._storage.get(user_id)

    def save_user_profile(self, profile: UserProfile) -> None:
        self._storage[profile.user_id] = profile
        self._persist()