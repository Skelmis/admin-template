from litestar.config.app import AppConfig
from litestar.di import Provide
from litestar.plugins import InitPlugin

from skelmis.admin.config import AdminConfiguration
from skelmis.admin.controllers import AdminController


class AdminPlugin(InitPlugin):
    def __init__(self, config: AdminConfiguration) -> None:
        self.config = config

    async def get_config(self) -> AdminConfiguration:
        return self.config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.route_handlers.append(AdminController)
        app_config.dependencies["plugin_config"] = Provide(self.get_config)
        return app_config
