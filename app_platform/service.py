import os
from config import settings


class PlatformService:

    def get_version(self) -> dict:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "build_hash": settings.BUILD_HASH,
        }

    def get_changelog(self) -> str:
        changelog_path = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")
        try:
            with open(changelog_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def get_banners(self) -> list:
        return []
