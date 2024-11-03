from fastapi import FastAPI, HTTPException, status

# Crear una instancia de la aplicación FastAPI
app = FastAPI()
app.title = "Remesas admin"
app.version = "0.1.0"

# Definir una ruta de prueba para verificar que todo esté funcionando
@app.get("/", tags="Inicio")
async def read_root():
    return {"message": "¡Bienvenido a FastAPI!"}

# Ruta de ejemplo con un parámetro de consulta
@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    if item_id == 1:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no autorizado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {"item_id": item_id, "q": q}
