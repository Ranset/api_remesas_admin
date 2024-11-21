from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from passlib.hash import bcrypt
from modulos.auth import create_access_token, authenticate_user, ResponseContract, User, Login, get_token, get_user
from modulos.models import session, Users

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
app.version = "0.3.3"

# Middleware implementation for CORS mannager
origins = [
    "http://localhost:8100",
    "https://cszk6rnz-8100.usw3.devtunnels.ms"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

# Enddpoint de registro de usuario
@app.post("/register", tags=["users"])
async def register(user: User):
    try:
        new_user = Users(email= user.email, password= bcrypt.hash(user.password), username= user.username)
        session.add(new_user)
        session.commit()
        user_data = get_user(user.email)
        user_data = {
            "id": user_data.id, 
            "email": user_data.email, 
            "username": user_data.username,
            "is_active": user_data.is_active,
            "updated_at": user_data.updated_at,
            }
        return ResponseContract(
            sucess= True,
            data= {
                'user': user_data
            }
        )
    except Exception as e:
        session.rollback()
        return ResponseContract(
            sucess= False,
            data= {
                'error': str(e.__cause__)
            }
        )
    finally:
        session.close()

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
        "id": user_data.id, 
        "email": user_data.email, 
        "username": user_data.username,
        "phone": user_data.phone_number, 
        "first_name": user_data.first_name, 
        "last_name": user_data.last_name,
        "avatar": user_data.avatar, 
        "is_active": user_data.is_active,
        "updated_at": user_data.updated_at,
        }

    response = ResponseContract(
        sucess= True,
        data= {
            'session': token, 
            'user': user_data
            }
    )

    return response

# Endpoint protegido que requiere el token JWT
@app.get("/protected")
async def protected_route(current_user: str = Depends(get_token)):
    """Testing protected endpoint
    """
    
    return ResponseContract(
        sucess= True,
        data= {
            "message": f"Hello, {current_user}"
            }
        )


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