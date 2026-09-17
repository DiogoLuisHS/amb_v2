def determine_file_layer(file: str) -> str:
    if "db/schema" in file or (
        "schema" in file and ("apps/api/src/db" in file or "src/db" in file)
    ):
        return "1_database_schemas"
    elif "repositories" in file or "repository" in file:
        return "2_repositories"
    elif "services" in file or "service" in file:
        return "3_services"
    elif "controllers" in file or "controller" in file:
        return "4_controllers"
    elif "routers" in file or "router" in file or "routes" in file:
        return "5_routers_api"
    elif ("apps/web" in file or "web" in file or "frontend" in file) and (
        "hooks" in file or "services" in file or "api" in file
    ):
        return "6_frontend_hooks_api"
    elif (
        "apps/web" in file or "web" in file or "frontend" in file
    ) and "components" in file:
        return "7_frontend_components"
    elif ("apps/web" in file or "web" in file or "frontend" in file) and (
        "pages" in file or "views" in file
    ):
        return "8_frontend_pages"
    else:
        return "9_entrypoints_config"
