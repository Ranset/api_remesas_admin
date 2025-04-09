from sqlalchemy import create_engine, Column, ForeignKey, Integer, Numeric, Boolean, Text, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import text
from pydantic import BaseModel
from typing import Optional
import datetime
import random
import string

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


class CreateOrder(BaseModel):
    owner_id: int
    group_id: int
    product_id: int
    user_id: int
    amount: int
    client_phone_number: str
    card_phone_number: str
    card_number: Optional[str] = None
    note: Optional[str] = None
    adress: Optional[str] = None

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
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    assigned_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    folio = Column(Text, unique=True, nullable=False)
    status = Column(Text, nullable=False, default='actived')
    open = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default='now()')
    amount = Column(Integer, nullable=False)
    card_num = Column(String(19))
    client_phone_number = Column(String, nullable=False)
    card_phone_number = Column(String, nullable=False)
    note = Column(Text)
    adress = Column(Text)

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


def get_orders_of_group(group_id: int) -> list:
    orders_list = []

    try:
        orders = session.query(Order).filter(Order.group_id == group_id).all()

        for order in orders:
            order_obj = {
                'id': order.id,
                'folio': order.folio,
                'owner_id': order.owner_id,
                'group_id': order.group_id,
                'product': {'id': order.product_id, 'name': get_product(order.product_id)},
                'user_id': order.assigned_user_id,
                'amount': order.amount,
                'client_phone_number': order.client_phone_number,
                'card_phone_number': order.card_phone_number,
                'card_number': order.card_num,
                'note': order.note,
                'adress': order.adress,
                'status': order.status,
                'open': order.open,
                'created_at': order.created_at
            }
            orders_list.append(order_obj)

        return orders_list

    finally:
        session.close()


def user_group_list(user_id: int) -> list:
    message = []

    query = (
        session.query(
            Group.id.label("group_id"),
            Group.name.label("group_name"),
            Group.description.label("group_desc"),
            Group.color.label("group_color"),
            Role.name.label("user_role")
        )
        .join(UserRole, Group.id == UserRole.group_id)
        .join(Role, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
    )

    group_result = query.all()
    session.close()

    groups_list = []

    for group in group_result:
        query = text(f"""
        SELECT u.id, u.username, u.email, u.first_name, u.last_name, r.id AS role_id, r.name AS role_name
        FROM user_roles ur
        JOIN users u ON ur.user_id = u.id
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.group_id = {group[0]}
        """)
        results = session.execute(query, {"group_id": group[0]}).fetchall()
        
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
            "id": group[0],
            "name": group[1],
            "description": group[2],
            "color": group[3],
            "users": group_users_list,
            "orders": get_orders_of_group(group[0])
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


def all_products_list() -> list:
    products_list = []

    try:
        products = session.query(Product).all()
    
        for product in products:
            products_list.append({"id": product.id, "name": product.name})
        
    except Exception as e:
        session.rollback()
        return [False, f"Error obtained products: {e}"]

    message = [True, products_list]

    return message


def generate_folio(leng= 20):
    # Fecha y hora en formato compacto
    timestamp = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    
    # Caracteres aleatorios
    caracteres_aleatorios = ''.join(random.choices(string.ascii_uppercase + string.digits, k=leng - len(timestamp)))
    
    # Generar el folio final
    folio = f"{timestamp}{caracteres_aleatorios}"
    
    # Ajustar la longitud si excede
    return folio[:leng]


def get_product(product_id: int):
    product = session.query(Product).filter(Product.id == product_id).first()

    if not product:
        session.close()
        return "Product not found"

    return product.name


def order_create(new_order_data: CreateOrder) -> list:
    message = []

    try:
        # Create new order
        db_order = Order(
            folio= generate_folio(15),
            owner_id= new_order_data.owner_id,
            group_id= new_order_data.group_id,
            product_id= new_order_data.product_id,
            assigned_user_id= new_order_data.user_id,
            amount= new_order_data.amount,
            client_phone_number= new_order_data.client_phone_number,
            card_phone_number= new_order_data.card_phone_number,
            card_num= new_order_data.card_number,
            note= new_order_data.note,
            adress= new_order_data.adress
        )
        session.add(db_order)
        session.commit()
        session.refresh(db_order)
        session.close()
    
    except Exception as e:
        session.rollback()
        message = [False, f"error in database {e}", None]
        return message

    order_object = {
        'id': db_order.id,
        'folio': db_order.folio,
        'owner_id': db_order.owner_id,
        'group_id': db_order.group_id,
        'product': {'id': db_order.product_id, 'name': get_product(db_order.product_id)},
        'user_id': db_order.assigned_user_id,
        'amount': db_order.amount,
        'client_phone_number': db_order.client_phone_number,
        'card_phone_number': db_order.card_phone_number,
        'card_number': db_order.card_num,
        'note': db_order.note,
        'adress': db_order.adress,
        'status': db_order.status,
        'open': db_order.open,
        'created_at': db_order.created_at
    }
    message = [True, "Order created successfully", order_object]
    
    return message


def order_update_executed (order_id: int) -> list:
    message = []

    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        message = [False, "The order does not exist", None]
        return message
    
    # Update field status
    order.status = "executed"

    session.commit()
    session.refresh(order)
    session.close()

    order_object = {
        'id': order.id,
        'folio': order.folio,
        'owner_id': order.owner_id,
        'group_id': order.group_id,
        'product': {'id': order.product_id, 'name': get_product(order.product_id)},
        'user_id': order.assigned_user_id,
        'amount': order.amount,
        'client_phone_number': order.client_phone_number,
        'card_phone_number': order.card_phone_number,
        'card_number': order.card_num,
        'note': order.note,
        'adress': order.adress,
        'status': order.status,
        'open': order.open,
        'created_at': order.created_at
    }
    message = [True, "Order updated successfully", order_object]

    return message


def order_update_canceled (order_id: int) -> list:
    message = []

    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        message = [False, "The order does not exist", None]
        return message
    
    # Update field status
    order.status = "cancelled"

    session.commit()
    session.refresh(order)
    session.close()

    order_object = {
        'id': order.id,
        'folio': order.folio,
        'owner_id': order.owner_id,
        'group_id': order.group_id,
        'product': {'id': order.product_id, 'name': get_product(order.product_id)},
        'user_id': order.assigned_user_id,
        'amount': order.amount,
        'client_phone_number': order.client_phone_number,
        'card_phone_number': order.card_phone_number,
        'card_number': order.card_num,
        'note': order.note,
        'adress': order.adress,
        'status': order.status,
        'open': order.open,
        'created_at': order.created_at
    }
    message = [True, "Order updated successfully", order_object]

    return message



if __name__ == "__main__":
    response = users_roles()
    print(response)
