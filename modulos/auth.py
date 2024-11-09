import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from supabase import Client, create_client
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SUPABASE_URL, SUPABASE_API_KEY

# Instancia Supabase
supabase: Client = create_client(SUPABASE_URL,SUPABASE_API_KEY)

# Dependencia de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    email: str
    password: str
    username: str

class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_from_db(email: str):
    response = supabase.table('users').select("*").eq('email', email).execute()
    if response.data:
        return response.data[0]
    return None


def authenticate_user(email: str, password: str):
    user = get_user_from_db(email)
    if user and user['password'] == password:  # Compara la contraseña (deberías encriptarla)
        return user
    return None


# def get_current_user(token: str = Depends(oauth2_scheme)):
def get_current_user(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except jwt.PyJWTError:
        raise credentials_exception