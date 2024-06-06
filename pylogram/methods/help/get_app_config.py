import asyncio
from typing import Any

import pylogram
from pylogram import raw
from pylogram.utils import telegram_json_to_python_obj


class GetAppConfig:
    async def get_app_config(
            self: "pylogram.Client",
            hash_: int = 0
    ) -> raw.base.help.AppConfig:
        return await self.invoke(raw.functions.help.GetAppConfig(hash=hash_))

    async def get_app_config_full(self) -> dict[str, Any]:
        hash_ = 0
        config_dict = {}

        while True:
            try:
                config = await self.get_app_config(hash_)

                if isinstance(config, raw.types.help.AppConfigNotModified):
                    break

                hash_ = config.hash
                config_dict.update(telegram_json_to_python_obj(config.config))
            except pylogram.errors.FloodWait as e:
                await asyncio.sleep(e.value)
                continue

        return dict(sorted(config_dict.items()))
