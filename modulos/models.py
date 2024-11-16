from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP

Base = declarative_base()

class User(Base):
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
from config import DB_URL, SUPABASE_DB_NAME, SUPABASE_USER, SUPABASE_PASSWORD

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
        users = session.query(User).all()
        for user in users:
            print(f"ID: {user.id}, Nombre: {user.username}, email: {user.email}")
    except Exception as e:
        print(f"Error in db connection: {e}")
    finally:
        # Cerrar la sesión
        session.close()

if __name__ == "__main__":
    prueba_conexion()