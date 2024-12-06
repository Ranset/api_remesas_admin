from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import Optional

# Pydantic
class User(BaseModel):
    email: str
    password: str
    username: str

class UserUpdate(BaseModel):
    avatar: Optional[str] = None
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class Login(BaseModel):
    email: str
    password: str

class UserGroupRole(BaseModel):
    user_id: int
    role_id: int

class CreateGroup(BaseModel):
    name: str
    description: str
    color: str
    users: list[UserGroupRole]

class UpdateGroup(BaseModel):
    id: int
    name: str
    description: str
    color: str
    users: list[UserGroupRole]


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


def user_by_nickname(nickname) -> list:
    user = session.query(Users).filter(Users.username == nickname).first()

    if not user:
        return [False, "User not found"]

    user_data = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "avatar": user.avatar
    }

    message = [True, user_data]

    return message


def users_roles() -> list:
    role_list = []

    try:
        roles = session.query(Role).all()
    
        for role in roles:
            role_list.append({"id": role.id, "name": role.name})
        
    except Exception as e:
        session.rollback()
        return [False, f"Error obtained roles: {e}"]

    message = [True, role_list]

    return message


def group_creation(group_data: CreateGroup):
    message = []

    try:
        # Create new group
        db_group = Group(name= group_data.name, description= group_data.description, color= group_data.color)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        session.close()
    
        # Asing users to group
        for user in group_data.users:
            db_roles = UserRole(user_id= user.user_id, group_id= db_group.id, role_id= user.role_id)
            session.add(db_roles)

        session.commit()
        session.close()
        
    except Exception as e:
        session.rollback()
        message = [False, f"error in database {e}", None]
        return message

    group_object = {
        'id': db_group.id,
        'name': db_group.name,
        'description': db_group.description,
        'color': db_group.color,
        'users': group_data.users
    }
    message = [True, "Group created successfully", group_object]
    
    return message


def get_group_details(group_id: int) -> list:
    group = session.query(Group).filter(Group.id == group_id).first()

    if not group:
        session.close()
        return [False, "The group does not exist"]
    
    query = text(f"""
        SELECT u.id, u.username, u.email, u.first_name, u.last_name, r.id AS role_id, r.name AS role_name
        FROM user_roles ur
        JOIN users u ON ur.user_id = u.id
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.group_id = {group.id}
    """)
    results = session.execute(query, {"group_id": group.id}).fetchall()
    
    group_users_list = []

    for result in results:
        user = result.tuple()

        role_obj = {
            "id": user[5],
            "name": user[6]
        }

        user_obj ={
            "id": user[0],
            "username": user[1],
            "first_name": user[3],
            "last_name": user[4],
            "role": role_obj
        }
        group_users_list.append(user_obj)

    group_obj = {
        "id": group.id,
        "name": group.name,
        "description": group.description,
        "color": group.color,
        "users": group_users_list
    }

    return [True, group_obj]




def group_update(group_data: UpdateGroup) -> list:
    message = []

    group = session.query(Group).filter(Group.id == group_data.id).first()
    if not group:
        message = [False, "The group does not exist", None]
        return message
    
    # Update all fields
    group.name = group_data.name
    group.description = group_data.description
    group.color = group_data.color

    session.commit()
    session.refresh(group)
    session.close()

    # update users group
    # first delete existing register of user group
    register_count = session.query(UserRole).filter(UserRole.group_id == group_data.id).delete()

    if register_count == 0:
        message = [False, f"No was users in this group. Group id: {group.id}", None]
        return message
    
    session.commit()
    session.close()

    # Add new users to group
    for user in group_data.users:
            db_roles = UserRole(user_id= user.user_id, group_id= group.id, role_id= user.role_id)
            session.add(db_roles)

    session.commit()
    session.close()

    group_object = {
        'id': group.id,
        'name': group.name,
        'description': group.description,
        'color': group.color,
        'users': group_data.users
    }
    message = [True, "Group updated successfully", group_object]

    return message


def user_group_list(user_id: int) -> list:
    message = []

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

    message = [True, groups_list]

    return message


def delete_group(group_id: int):
    group_to_delete = session.query(Group).filter(Group.id == group_id).first()

    message = []

    if group_to_delete:
        session.delete(group_to_delete)
        session.commit()
        message = [True, "Group deleted successfully"]
    else:
        message = [False, "Group not found"]

    session.close()
    return message


if __name__ == "__main__":
    # prueba_conexion()
    response = users_roles()
    print(response)
