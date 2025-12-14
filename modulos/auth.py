import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from passlib.hash import bcrypt
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .models import session, Users, ResponseContract

# Define the security scheme for API Key in the Authorization header
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user(email: str):
    try:
        response = session.query(Users).filter_by(email = email).first()
        if response:
            return response
        return None
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

def get_user_data(email: str) -> dict:
    user_data = get_user(email)
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
        "notify": user_data.notify,
        "device_token": user_data.device_token,
        "mail_code": True if user_data.mail_code else False
        }
    
    return user_data


def authenticate_user(email: str, password: str):
    user = get_user(email)

    if not user:
        return None

    if not user.password:
        return None

    if user:
        if bcrypt.verify(password, user.password):
            return user
    return None


# Function to retrieve and validate the token
def get_token(api_key: str = Security(api_key_header)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token missing",
        )
    
    # Separate the Bearer scheme and the token
    try:
        scheme, token = api_key.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return email
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization format")
    

def verify_code(user_email: str, code: str):
    try:
        user = session.query(Users).filter(Users.email == user_email).first()
        if not user:
            return (False, 'User not found')
        
        mail_code = str(user.mail_code)
        
        if mail_code[-4:] != code:
            return (False, 'Invalid verification code')
        
        ts_str = mail_code[:-4]  # parte de timestamp YYYYMMDDhhmmss
        code_dt = datetime.strptime(ts_str, "%Y%m%d%H%M%S")

        # Verificar si el código ha expirado (más de 24 horas)
        if datetime.now() - code_dt > timedelta(hours=24):
            return (False, 'Verification code has expired')
        
    except Exception as e:
        session.rollback()
        return (False, str(e.__cause__))
    
    finally:
        session.close()

    return (True, 'Code verified successfully')