from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from passlib.hash import bcrypt
from modulos.auth import create_access_token, authenticate_user, get_token, get_user
from modulos.models import session, Users, delete_user, update_user, ResponseContract, User, UserUpdate, Login

tags_metadata = [
    {
        "name": "auth",
        "description": "The **login** logic is here.",
    },
    {
        "name": "users",
        "description": "Operations with users.",
    },
    {
        "name": "groups",
        "description": "Operations with groups.",
    },
    ]

# Crear una instancia de la aplicación FastAPI
app = FastAPI(openapi_tags=tags_metadata)
app.title = "Remesas admin"
app.version = "0.4.3"

# Middleware implementation for CORS mannager
origins = [
    "http://localhost:8100",
    "https://cszk6rnz-8100.usw3.devtunnels.ms", #tunnel tests
    "http://127.0.0.1:5500" #local tests
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )


# Enddpoint de registro de usuario
@app.post("/api/auth/register", tags=["auth"])
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
@app.post("/api/auth/login", response_model=ResponseContract, tags=["auth"])
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


# Endpoint User data update
@app.patch("/api/user/update/{user_id}", response_model= ResponseContract, tags= ["users"])
async def user_update(user_id: int, user_patch: UserUpdate, current_user: str = Depends(get_token)):
    response = update_user(user_id, user_patch)

    return ResponseContract(
        sucess= response[0],
        data= {
            'message': response[1]
        }
    )


# Endpoint delete User
@app.delete("/api/user/delete/{user_id}", response_model= ResponseContract, tags= ["users"])
async def user_delete(user_id: int, current_user: str = Depends(get_token)):
    response = delete_user(user_id)
    return ResponseContract(
        sucess= response[0],
        data= {
            'message': response[1] 
        }
    )


# Endpoint protegido que requiere el token JWT
@app.get("/api/protected")
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