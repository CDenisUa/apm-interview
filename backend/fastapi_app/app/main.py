"""FastAPI application entrypoint — wires REST + GraphQL + CORS."""
# Core
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
# Local
from .rest import router as rest_router
from .todo_rest import router as todo_router
from .schema import schema

app = FastAPI(title="Business Modernization Portal — FastAPI service")

# CORS for the React dev servers. Demo-wide open; restrict in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Served-By"],
)


@app.middleware("http")
async def served_by(request: Request, call_next):
    """Tag every response so the frontend can show which backend answered."""
    response = await call_next(request)
    response.headers["X-Served-By"] = "fastapi"
    return response


app.include_router(rest_router)
app.include_router(todo_router)
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.get("/")
def root():
    return {
        "service": "fastapi",
        "endpoints": {
            "health": "/api/health",
            "rest_items": "/api/items",
            "rest_todos": "/api/todos",
            "graphql": "/graphql",
            "docs": "/docs",
        },
    }
