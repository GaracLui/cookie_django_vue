from ninja import NinjaAPI
from ninja.openapi.docs import Swagger, Redoc  # Import the doc renderers

api = NinjaAPI(
    title="Website backend API",
    version="0.1.0",
    description="Backend for Vue.js frontend",
    docs=Swagger(),   # Instead of docs="swagger"
    # docs=Redoc(),   # Alternative if you prefer Redoc
)

@api.get("/health")
def health_check(request):
    return {"status": "ok"}
