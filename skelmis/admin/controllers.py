from litestar import Controller, get, Request
from litestar.response import Template, Redirect

from skelmis.admin.config import AdminConfiguration
from skelmis.admin.html import html_template, alert


class AdminController(Controller):
    path = "/"

    @get("/", name="admin_home")
    async def get_home_page(self, plugin_config: AdminConfiguration) -> Template:
        data = []
        for row in plugin_config.home_ui:
            data.append((row.name, row.description, await row.count_rows(), row.slug))
        return html_template(
            "home.jinja", context={"config": plugin_config, "data": data}
        )

    @get("/tables/{slug:str}", name="table_view")
    async def get_table_home(
        self, request: Request, plugin_config: AdminConfiguration, slug: str
    ) -> Template | Redirect:
        table = plugin_config.get_table(slug)
        if table is None:
            alert(request, "Table not found", level="error")
            return Redirect(request.url_for("admin_home"))

        return html_template(
            "table/view_all.jinja",
            context={
                "config": plugin_config,
                "table": table,
                "data": await table.list_rows(),
            },
        )

    @get("/tables/{slug:str}/{row_id:str}", name="table_view_row")
    async def get_table_row(
        self,
        request: Request,
        plugin_config: AdminConfiguration,
        slug: str,
        row_id: str,
    ) -> Template | Redirect:
        table = plugin_config.get_table(slug)
        if table is None:
            alert(request, "Table not found", level="error")
            return Redirect(request.url_for("admin_home"))

        return html_template(
            "table/view_one.jinja",
            context={
                "config": plugin_config,
                "table": table,
                "data": await table.list_rows(),
            },
        )
