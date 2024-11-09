from fastapi import FastAPI, HTTPException, Depends
from datetime import timedelta
from modulos.auth import create_access_token, authenticate_user, get_current_user, Token, User, supabase, Login

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "Remesas groups",
        "description": "Operations with groups.",
    },
    ]

# Crear una instancia de la aplicación FastAPI
app = FastAPI(openapi_tags=tags_metadata)
app.title = "Remesas admin"
app.version = "0.3.0"

# Enddpoint de registro de usuario
@app.post("/register", tags=["users"])
async def register(user: User):
    response = supabase.table('users').insert({"email": user.email, "password": user.password, "username": user.username}).execute()
    return {"message": "User created successfully"}
    # if response.status_code == 201:
    #     return {"message": "User created successfully"}
    # raise HTTPException(status_code=400, detail="User already exists")

# Endpoint de login
@app.post("/login", response_model=Token, tags=["users"])
async def login(user: Login):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint protegido que requiere el token JWT
@app.get("/protected")
async def protected_route(current_user: str = Depends(get_current_user)):
    """Testing protected endpoint
    """
    
    return {"message": f"Hello, {current_user}"}

"""
# Modelo de respuesta para endpoint
class GroupResponse(BaseModel):
    group_id: int
    group_name: str
    group_description: str
    
# Definir una ruta de prueba para verificar que todo esté funcionando
@app.get("/get-groups", tags=["groups"])
async def get_all_groups():
    response = (
        supabase
        .table("groups")
        .select("name","id","description")
        .execute()
    )

    result = []
    for record in response.data:
        result.append(GroupResponse(
            group_id = record["id"],
            group_name = record["name"],
            group_description= record["description"]
        ))
    return result




# Ruta de ejemplo con un parámetro de consulta
# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: str = None):
#     if item_id == 1:
#         raise HTTPException(
#             status_code= status.HTTP_401_UNAUTHORIZED,
#             detail="Usuario no autorizado",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     return {"item_id": item_id, "q": q}
"""