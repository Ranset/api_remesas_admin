from fastapi import FastAPI, HTTPException, Depends,status
from datetime import timedelta
from modulos.auth import create_access_token, authenticate_user, ResponseContract, User, supabase, Login, get_token, get_user
from passlib.hash import bcrypt

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "groups",
        "description": "Operations with groups.",
    },
    ]

# Crear una instancia de la aplicación FastAPI
app = FastAPI(openapi_tags=tags_metadata)
app.title = "Remesas admin"
app.version = "0.3.2"

# Enddpoint de registro de usuario
@app.post("/register", tags=["users"])
async def register(user: User):
    try:
        response = supabase.table('users').insert({"email": user.email, "password": bcrypt.hash(user.password), "username": user.username}).execute()
        return {"message": "User created successfully"}
        # if response.status_code == 201:
        #     return {"message": "User created successfully"}
        # raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail= f"Error in registration: {e.details}")

# Endpoint de login
@app.post("/login", response_model=ResponseContract, tags=["users"])
async def login(user: Login):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    token = {"access_token": access_token, "token_type": "bearer"}

    user_data = get_user(user.email)
    user_data = {
        "user_id": user_data[0]["id"], 
        "user_email": user_data[0]["email"], 
        "username": user_data[0]["username"],
        "user_phone": user_data[0]["phone_number"], 
        "first_name": user_data[0]["first_name"], 
        "last_name": user_data[0]["last_name"],
        "user_avatar": user_data[0]["avatar"], 
        "is_active": user_data[0]["is_active"],
        "user_updated_at": user_data[0]["updated_at"],
        }

    response = ResponseContract(
        sucess= True,
        data= [token, user_data]
    )

    return response

# Endpoint protegido que requiere el token JWT
@app.get("/protected")
async def protected_route(current_user: str = Depends(get_token)):
    """Testing protected endpoint
    """
    
    return ResponseContract(sucess= True, data= [{"message": f"Hello, {current_user}"}])


"""
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