from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app_platform.service import PlatformService

router = APIRouter(prefix="/platform", tags=["platform"])


def _get_platform_service() -> PlatformService:
    return PlatformService()


@router.get("/version")
async def get_version(svc: PlatformService = Depends(_get_platform_service)):
    return svc.get_version()


@router.get("/changelog", response_class=PlainTextResponse)
async def get_changelog(svc: PlatformService = Depends(_get_platform_service)):
    return svc.get_changelog()


@router.get("/banners")
async def get_banners(svc: PlatformService = Depends(_get_platform_service)):
    return svc.get_banners()
