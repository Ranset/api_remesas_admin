from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from pydantic import BaseModel

# Pydantic
class User(BaseModel):
    email: str
    password: str
    username: str

class UserUpdate(BaseModel):
    avatar: str = None
    phone_number: str = None
    first_name: str = None
    last_name: str = None

class Login(BaseModel):
    email: str
    password: str

class ResponseContract(BaseModel):
    sucess: bool
    data: dict

# End Pydantic


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(Text, nullable=True)
    avatar = Column(Text, nullable=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    first_name = Column(Text, nullable=True)
    last_name = Column(Text, nullable=True)
    username = Column(Text, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default='now()')
    updated_at = Column(TIMESTAMP, default='now()')

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(Text, nullable=True)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Text, nullable=True)

class Role(Base):
    __tablename__ = 'roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)

class AuthToken(Base):
    __tablename__ = 'auth_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(Text, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, default='now()')
    expires_at = Column(TIMESTAMP, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    created_at = Column(TIMESTAMP, default='now()')
    assigned_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    open = Column(Boolean, default=False)
    folio = Column(Text, nullable=False, unique=True)
    status = Column(Text, nullable=False, default='created')

class UserRole(Base):
    __tablename__ = 'user_roles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    # __table_args__ = (UniqueConstraint('user_id', 'group_id', name='_user_group_uc'),)

# Conections methods
from .config import DB_URL, SUPABASE_DB_NAME, SUPABASE_USER, SUPABASE_PASSWORD

# Create URL connection for SQLAlchemy
DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{DB_URL}/{SUPABASE_DB_NAME}"

# Create engine for SQLAlchemy
engine = create_engine(DATABASE_URL)

# Create session
Session = sessionmaker(bind=engine)
session = Session()

def prueba_conexion ():
    # Consultar datos usando modelos
    try:
        # Consultar todos los productos
        users = session.query(Users).all()
        for user in users:
            print(f"ID: {user.id}, Nombre: {user.username}, email: {user.email}")
    except Exception as e:
        print(f"Error in db connection: {e}")
    finally:
        # Cerrar la sesión
        session.close()


def delete_user(user_id: int):
    user_to_delete = session.query(Users).filter(Users.id == user_id).first()
    print("El objeto:",user_to_delete)
    message = []

    if user_to_delete:
        session.delete(user_to_delete)
        session.commit()
        message = [True, "User deleted successfully"]
    else:
        message = [False, "User not found"]

    session.close()
    return message


def update_user(user_id: int, user_patch: UserUpdate):
    message = []

    user = session.query(Users).filter(Users.id == user_id).first()

    if not user:
        message = [False, "User not found"]
        session.close()
        return message

    #update user fields
    update_data = user_patch.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    session.commit()
    session.refresh(user)
    session.close()

    message = [True, "User data updated successfully"]

    return message


if __name__ == "__main__":
    # prueba_conexion()
    response = session.query(Users).filter_by(email = "yo@yo.com").first()
    print(response.email)
