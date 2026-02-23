from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, admin_category, admin_dish, admin_restaurant, public_menu






app = FastAPI()

# Incluye routers con prefijos claros
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(admin_category.router, prefix="/api/v1/admin/categories")
app.include_router(admin_dish.router, prefix="/api/v1/admin/dishes", tags=["dishes"])
app.include_router(admin_restaurant.router, prefix="/api/v1/admin/restaurants")
app.include_router(public_menu.router)




# Debug: imprime todas las rutas registradas
for route in app.routes:
    print(route.path, route.methods)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}