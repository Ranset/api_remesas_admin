from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from passlib.hash import bcrypt
from modulos.auth import create_access_token, authenticate_user, get_token, get_user, get_user_data
from modulos.models import session, Users, Group, delete_user, update_user, create_group, ResponseContract, User, UserRole, UserUpdate, Login, CreateGroup, Role

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
app.version = "0.4.6"

# Middleware implementation for CORS mannager
origins = [
    "http://localhost:8100",
    "https://cszk6rnz-8100.usw3.devtunnels.ms", #tunnel tests
    "http://127.0.0.1:5500", #local tests
    "capacitor://localhost", # Para apps Ionic con Capacitor
    "ionic://localhost",     # Para apps con Ionic
]

origins = ["*"]

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

    user_data = get_user_data(user.email)

    response = ResponseContract(
        sucess= True,
        data= {
            'session': token, 
            'user': user_data
            }
    )

    return response


# Endpoint User data update
@app.patch("/api/user/{user_id}", response_model= ResponseContract, tags= ["users"])
async def user_update(user_id: int, user_patch: UserUpdate, current_user: str = Depends(get_token)):
    response = update_user(user_id, user_patch)

    user_data = get_user_data(current_user)

    return ResponseContract(
        sucess= response[0],
        data= {
            'message': response[1],
            'user': user_data
        }
    )


# Endpoint delete User
@app.delete("/api/user/{user_id}", response_model= ResponseContract, tags= ["users"])
async def user_delete(user_id: int, current_user: str = Depends(get_token)):
    response = delete_user(user_id)
    return ResponseContract(
        sucess= response[0],
        data= {
            'message': response[1] 
        }
    )


# Endpoint create group
@app.post("/api/groups/", response_model=ResponseContract, tags=["groups"])
async def create_group(new_group_data: CreateGroup, current_user: str = Depends(get_token)):
    
    try:
        # Create new group
        db_group = Group(name= new_group_data.group_name, description= new_group_data.group_description, color= new_group_data.group_color)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        session.close()
    
        # Asing users to group
        for user in new_group_data.group_users:
            db_roles = UserRole(user_id= user.user_id, group_id= db_group.id, role_id= user.role_id)
            session.add(db_roles)

        session.commit()
        session.close()
        
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="error inserting")

    return ResponseContract(
        sucess= True,
        data={
            "message": db_group.id
        }
    )


# Endpoint list group
@app.get("/api/groups/{user_id}", response_model=ResponseContract, tags=["groups"])
async def get_user_groups(user_id: int, current_user: str = Depends(get_token)):
    """Gets the groups a user belongs to
    """

    query = (
        session.query(
            Group.id.label("group_id"),
            Group.name.label("group_name"),
            Role.name.label("user_role")
        )
        .join(UserRole, Group.id == UserRole.group_id)
        .join(Role, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
    )

    result = query.all()

    groups_list = []

    for group in result:
        group_obj = {
            "id": group[0],
            "name": group[1],
            "role": group[2]
        }

        groups_list.append(group_obj)

    return ResponseContract(
        sucess= True,
        data= {
            "groups": groups_list
        }
    )


# Endpoint update group
@app.put("/api/groups/", response_model=ResponseContract, tags=["groups"])
async def update_group(current_user: str = Depends(get_token)):
    pass


# Endpoint delete group
@app.delete("/api/groups/", response_model=ResponseContract, tags=["groups"])
async def delete_group(current_user: str = Depends(get_token)):
    pass
