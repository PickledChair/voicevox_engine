"""設定機能を提供する API Router"""

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.templating import Jinja2Templates

from voicevox_engine.engine_manifest import BrandName
from voicevox_engine.setting.Setting import CorsPolicyMode, Setting, SettingHandler
from voicevox_engine.utility.path_utility import resource_root

from ..dependencies import check_disabled_mutable_api

_setting_ui_template = Jinja2Templates(
    directory=resource_root(),
    variable_start_string="<JINJA_PRE>",
    variable_end_string="<JINJA_POST>",
)


def generate_setting_router(
    setting_loader: SettingHandler, brand_name: BrandName
) -> APIRouter:
    """設定 API Router を生成する"""
    router = APIRouter(tags=["設定"])

    @router.get("/setting", response_class=Response)
    def setting_get(request: Request) -> Response:
        """
        設定ページを返します。
        """
        settings = setting_loader.load()

        cors_policy_mode = settings.cors_policy_mode
        allow_origin = settings.allow_origin

        if allow_origin is None:
            allow_origin = ""

        return _setting_ui_template.TemplateResponse(
            "setting_ui_template.html",
            {
                "request": request,
                "brand_name": brand_name,
                "cors_policy_mode": cors_policy_mode.value,
                "allow_origin": allow_origin,
            },
        )

    @router.post(
        "/setting", status_code=204, dependencies=[Depends(check_disabled_mutable_api)]
    )
    def setting_post(
        cors_policy_mode: Annotated[CorsPolicyMode, Form()],
        allow_origin: Annotated[str | None, Form()] = None,
    ) -> None:
        """
        設定を更新します。
        """
        settings = Setting(
            cors_policy_mode=cors_policy_mode,
            allow_origin=allow_origin,
        )

        # 更新した設定へ上書き
        setting_loader.save(settings)

    return router
