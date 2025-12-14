from fastapi import FastAPI, HTTPException, Depends,status
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta, datetime
from passlib.hash import bcrypt
from modulos.auth import create_access_token, authenticate_user, get_token, get_user, get_user_data, verify_code
from modulos.mailjet_email import MailjetEmail
from modulos.statics import get_order_statistics, download_statics_excel
from modulos.date_utility import DateUtlility
from modulos.models import (session, 
                            Users, 
                            Group, 
                            delete_user, 
                            delete_group, 
                            update_user, 
                            group_creation,
                            get_group_details,
                            group_update,
                            user_group_list,
                            users_roles,
                            user_by_nickname,
                            order_create,
                            all_products_list,
                            order_update,
                            send_new_order_notification,
                            ResponseContract, 
                            User, 
                            UserUpdate, 
                            Login, 
                            CreateGroup,
                            UpdateGroup,
                            CreateOrder,
                            Email,
                            VerifyEmail,
                            ForgotPassword
                            )

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
    {
        "name": "orders",
        "description": "Orders's objects and related, like products, etc.",
    },
    {
        "name": "Stats",
        "description": "Statistics related to groups.",
    },
    ]

# Crear una instancia de la aplicación FastAPI
app = FastAPI(openapi_tags=tags_metadata)
app.title = "Remesas admin"
app.version = "0.8.2"

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
@app.post("/api/auth/register", tags=["auth"], response_model=ResponseContract)
async def register(user: User):
    try:
        code = DateUtlility().generar_codigo()
        new_user = Users(email= user.email, password= bcrypt.hash(user.password), username= user.username, mail_code= code, is_active= False)
        session.add(new_user)
        session.commit()
        user_data = get_user(user.email)
        user_data = {
            "id": user_data.id, 
            "email": user_data.email, 
            "username": user_data.username,
            "is_active": user_data.is_active,
            "updated_at": user_data.updated_at,
            "mail_code": True if user_data.mail_code else False
            }
        
        email_code = MailjetEmail()
        email_code.send_email_verify(code[-4:], user_data["email"], user_data["username"])  # Send only the last 4 digits as code, email and username

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

#Ebdpoint reenviar código de verificación
@app.post("/api/auth/resend_verification_code", response_model=ResponseContract, tags=["auth"])
async def resend_verification_code(email: Email):
    try:
        code = DateUtlility().generar_codigo()

        user_data = get_user(email.email)
        user_data = {
            "id": user_data.id, 
            "email": user_data.email, 
            "username": user_data.username,
            "is_active": user_data.is_active,
            "updated_at": user_data.updated_at,
            "mail_code": True if user_data.mail_code else False
            }
        
        email_code = MailjetEmail()
        email_code.send_email_verify(code[-4:], user_data["email"], user_data["username"])  # Send only the last 4 digits as code, email and username

        return ResponseContract(
            sucess= True,
            data= {
                'message': 'Verification code resent successfully'
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

#Endpoint para verificar el código de usuario
@app.post("/api/auth/verify_email", response_model=ResponseContract, tags=["auth"])
async def verify_email(verify_email: VerifyEmail):
    
    verify = verify_code(verify_email.email, verify_email.code)

    if verify[0]:
        user = session.query(Users).filter(Users.email == verify_email.email).first()
        user.mail_code = None  # Clear the mail_code to indicate verification
        user.is_active = True
        session.commit()

        email_welcome = MailjetEmail()
        email_welcome.send_email_welcome(user.email, user.username)
        
        session.close()

    return ResponseContract(
        sucess= verify[0],
        data= {
            'message': verify[1]
        }
    )
    

# Endpoint para enviar email de restablecimiento de contraseña
@app.post("/api/auth/forgot_password", response_model=ResponseContract, tags=["auth"])
async def forgot_password(forgot: ForgotPassword):
    user = get_user(forgot.email)

    if not user:
        return ResponseContract(
            sucess= False,
            data= {
                'message': 'User not found'
            }
        )

    if user.password is None:
        user = session.query(Users).filter(Users.email == forgot.email).first()
        if user:
            user.password = bcrypt.hash(forgot.code_or_password)
            session.commit()
            session.refresh(user)  # Refresca el objeto para asegurar que se guardó

            email_new_password = MailjetEmail()
            email_new_password.send_email_new_password(user.email, user.username)

            session.close()

            return ResponseContract(
                sucess=True,
                data={
                    'message': 'Password has been reset successfully'
                }
            )
        else:
            return ResponseContract(
                sucess=False,
                data={
                    'message': 'User not found'
                }
            )

    if len(forgot.code_or_password) == 4 and user.mail_code != None:        
        verify = verify_code(user.email, forgot.code_or_password)

        if verify[0]:
            user = session.query(Users).filter(Users.id == user.id).first()
            user.mail_code = None  # Clear the mail_code to indicate verification
            user.password = None  # Set password to None to force reset
            session.commit()            
            session.close()

        return ResponseContract(
            sucess= verify[0],
            data= {
                'message': verify[1]
            }
        )

        
    code = DateUtlility().generar_codigo()
    user = session.query(Users).filter(Users.email == forgot.email).first()
    user.mail_code = code
    session.commit()

    email_reset = MailjetEmail()
    email_reset.send_email_password_reset(code[-4:], user.email, user.username)  # Send only the last 4 digits as code, email and username

    session.close()

    return ResponseContract(
        sucess= True,
        data= {
            'message': 'Password reset code sent to email'
        }
    )
    


# Endpoint de login
@app.post("/api/auth/login", response_model=ResponseContract, tags=["auth"])
async def login(user: Login):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")
    
    access_token_expires = timedelta(days=7)
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


# Endpoint obtain user data by nickname
@app.get("/api/user/{nickname}", response_model= ResponseContract, tags= ["users"])
async def get_user_by_nickname(nickname: str, current_user: str = Depends(get_token)):
    response = user_by_nickname(nickname)

    return ResponseContract(
        sucess= response[0],
        data= {
            'user': response[1] 
        }
    )


# Endpoint obtain all roles
@app.get("/api/user/roles/getall", response_model= ResponseContract, tags= ["users"])
async def get_users_roles(current_user: str = Depends(get_token)):
    response = users_roles()

    return ResponseContract(
        sucess= response[0],
        data= {
            'roles': response[1] 
        }
    )


# Endpoint create group
@app.post("/api/groups", response_model=ResponseContract, tags=["groups"])
async def create_group(new_group_data: CreateGroup, current_user: str = Depends(get_token)):
    
    response = group_creation(new_group_data)

    return ResponseContract(
        sucess= response[0],
        data={
            "message": response[1],
            "group": response[2]
        }
    )


# Endpoint get group details
@app.get("/api/groups/{group_id}", response_model=ResponseContract, tags=["groups"])
async def get_group(group_id: int, current_user: str = Depends(get_token)):
    """Get group object
    """

    response = get_group_details(group_id)

    return ResponseContract(
        sucess= response[0],
        data= {
            "group": response[1]
        }
    )


# Endpoint list user groups
@app.get("/api/groups/user/{user_id}", response_model=ResponseContract, tags=["groups"])
async def get_user_groups(user_id: int, current_user: str = Depends(get_token)):
    """Gets the groups a user belongs to
    """

    response = user_group_list(user_id)

    return ResponseContract(
        sucess= response[0],
        data= {
            "groups": response[1]
        }
    )


# Endpoint update group
@app.put("/api/groups", response_model=ResponseContract, tags=["groups"])
async def update_group(new_group_data: UpdateGroup, current_user: str = Depends(get_token)):
    
    response = group_update(new_group_data)

    return ResponseContract(
        sucess= response[0],
        data={
            "message": response[1],
            "group": response[2]
        }
    )


# Endpoint delete group
@app.delete("/api/groups/{group_id}", response_model= ResponseContract, tags=["groups"])
async def group_delete(group_id: int, current_user: str = Depends(get_token)):
    response = delete_group(group_id)

    return ResponseContract(
        sucess= response[0],
        data= {
            'message': response[1] 
        }
    )


# Endpoint list products
@app.get("/api/order/products", response_model=ResponseContract, tags=["orders"])
async def get_products(current_user: str = Depends(get_token)):
    """Gets the products list a user can order
    """

    response = all_products_list()

    return ResponseContract(
        sucess= response[0],
        data= {
            "products": response[1]
        }
    )


# Endpoint create order
"""
Para pruebas
{
  "owner_id": 69,
  "group_id": 43,
  "product_id": 1,
  "user_id": 10,
  "amount": 909,
  "client_phone_number": "9988800833",
  "card_phone_number": "123456789112",
  "card_number": "52689584",
  "note": "",
  "adress": ""
}
"""
@app.post("/api/order", response_model=ResponseContract, tags=["orders"])
async def create_order(new_order_data: CreateOrder, current_user: str = Depends(get_token)):
    
    response = order_create(new_order_data)

    notify = send_new_order_notification(response[2]["user_id"], response[2]["folio"], response[2]["group_id"], response[2]["id"])

    return ResponseContract(
        sucess= response[0],
        data={
            "message": response[1],
            "order": response[2],
            "notification": notify
        }
    )


# @app.patch("/api/order/executed/{order_id}", response_model=ResponseContract, tags=["orders"])
# async def order_executed(order_id: int, current_user: str = Depends(get_token)):
    
#     response = order_update_executed(order_id)

#     return ResponseContract(
#         sucess= response[0],
#         data={
#             "message": response[1],
#             "order": response[2]
#         }
#     )


# @app.patch("/api/order/canceled/{order_id}", response_model=ResponseContract, tags=["orders"])
# async def order_canceled(order_id: int, current_user: str = Depends(get_token)):
    
#     response = order_update_canceled(order_id)

#     return ResponseContract(
#         sucess= response[0],
#         data={
#             "message": response[1],
#             "order": response[2]
#         }
#     )

# Endpoint para actualizar orden
@app.put("/api/order/{order_id}", response_model=ResponseContract, tags=["orders"])
async def update_order(order_id: int, new_order_data: CreateOrder, current_user: str = Depends(get_token)):
    
    response = order_update(order_id, new_order_data)

    return ResponseContract(
        sucess= response[0],
        data={
            "message": response[1],
            "order": response[2]
        }
    )


# Endpoint get statics for orders in the last 3 months
@app.get("/api/order/statics/{group_id}", response_model=ResponseContract, tags=["Stats"])
async def statics(group_id: int, current_user: str = Depends(get_token)):
    """Gets the statistics for orders in the last 3 months
    """

    response = get_order_statistics(group_id)

    return ResponseContract(
        sucess= response[0],
        data= {
            "statistics": response[1]
        }
    )


# Endpoint download statics Excel
@app.get("/api/order/statics/{group_id}/download", response_model=ResponseContract, tags=["Stats"])
async def download_statics(group_id: int, current_user: str = Depends(get_token)):
    """Downloads the statistics for orders in the last 3 months as an Excel file
    """

    response = download_statics_excel(group_id)
    if not response:
        return ResponseContract(
            sucess=False,
            data={
                "message": "Error generating Excel file"
            }
        )

    # return ResponseContract(
    #     sucess=True,
    #     data={
    #         "file": response
    #     }
    # )

    return response
