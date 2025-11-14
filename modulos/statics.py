from .models import session, Order, Product
import datetime
from sqlalchemy import func

def get_order_statistics(group_id: int):
    now = datetime.datetime.now()
    three_months_ago = now - datetime.timedelta(days=90)

    # Pre-cargar productos
    products = {p.id: p.name for p in session.query(Product).all()}

    # Obtener órdenes de los últimos 3 meses
    orders = (
        session.query(Order)
        .filter(
            Order.created_at >= three_months_ago,
            Order.group_id == group_id
        )
        .all()
    )

    # Agrupar por mes
    stats_by_month = {}
    for order in orders:
        month_key = order.created_at.strftime("%B")
        if month_key not in stats_by_month:
            stats_by_month[month_key] = {
                "month": month_key,
                "orders": {
                    "total": 0,
                    "totalAmount": 0,
                    "byStatus": {},
                    "byProduct": {}
                }
            }
        stats_by_month[month_key]["orders"]["total"] += 1
        stats_by_month[month_key]["orders"]["totalAmount"] += float(order.amount) if order.amount else 0

        # Agrupar por status
        status = order.status
        if status not in stats_by_month[month_key]["orders"]["byStatus"]:
            stats_by_month[month_key]["orders"]["byStatus"][status] = 0
        stats_by_month[month_key]["orders"]["byStatus"][status] += 1

        # Agrupar por producto
        product_id = order.product_id
        if product_id not in stats_by_month[month_key]["orders"]["byProduct"]:
            stats_by_month[month_key]["orders"]["byProduct"][product_id] = 0
        stats_by_month[month_key]["orders"]["byProduct"][product_id] += 1

    # Formatear la respuesta final
    status_names = {
        "executed": "Ejecutada",
        "active": "Activa",
        "cancelled": "Cancelada"
    }
    result = []
    for month, data in stats_by_month.items():
        total_orders = data["orders"]["total"]
        by_status = []
        for status, value in data["orders"]["byStatus"].items():
            percentage = round((value / total_orders) * 100, 2) if total_orders else 0 
            by_status.append({
                "status": {
                    "name": status_names.get(status, status),
                    "value": status
                },
                "value": value,
                "percentage": percentage
            })
        by_product = []
        for product_id, value in data["orders"]["byProduct"].items():
            percentage = round((value / total_orders) * 100, 2) if total_orders else 0
            by_product.append({
                "product": {
                    "id": product_id,
                    "name": products.get(product_id, "")
                },
                "value": value,
                "percentage": percentage
            })
        result.append({
            "month": month,
            "orders": {
                "total": total_orders,
                "totalAmount": data["orders"]["totalAmount"],
                "byStatus": by_status,
                "byProduct": by_product
            }
        })

    session.close()
    return [True, result]


def get_order_statistics_detailed(group_id: int):
    """
    Devuelve una lista de órdenes ejecutadas y canceladas de los últimos 3 meses,
    con los campos detallados por orden.
    """
    from .models import Product, Users

    now = datetime.datetime.now()
    three_months_ago = now - datetime.timedelta(days=90)

    # Pre-cargar productos y usuarios para evitar múltiples queries
    products = {p.id: p.name for p in session.query(Product).all()}
    users = {u.id: f"{u.first_name} {u.last_name}" for u in session.query(Users).all()}

    orders = (
        session.query(Order)
        .filter(
            Order.created_at >= three_months_ago,
            Order.status.in_(["executed", "cancelled"]),
            Order.group_id == group_id
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    executed = []
    cancelled = []

    for order in orders:
        order_data = {
            "card_num": order.card_num,
            "product": {
                "id": order.product_id,
                "name": products.get(order.product_id, "")
            },
            "amount": float(order.amount) if order.amount else 0,
            "created_at": order.created_at,
            "assigned_user": {
                "id": order.assigned_user_id,
                "name": users.get(order.assigned_user_id, "")
            },
            "folio": order.folio,
            "client_phone_number": order.client_phone_number,
            "card_phone_number": order.card_phone_number,
            "note": order.note,
            "owner": {
                "id": order.owner_id,
                "name": users.get(order.owner_id, "")
            }
        }
        if order.status == "executed":
            executed.append(order_data)
        elif order.status == "cancelled":
            cancelled.append(order_data)

    session.close()
    message = [True, {"executed": executed, "cancelled": cancelled}]
    return message


def download_statics_excel(group_id: int):
    """Generates an Excel file with the order statistics for the last 3 months."""
    from openpyxl import Workbook
    from fastapi.responses import StreamingResponse
    import io

    response = get_order_statistics_detailed(group_id)
    if not response[0]:
        return None

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Order Statistics"

    headers = [
        "Folio", "Producto", "Estado", "Número tarjeta", "Cantidad", "Fecha de creación",
        "Usuario Asignado", "Teléfono Cliente", "Teléfono Tarjeta", "Creador",
        "Nota"
    ]
    sheet.append(headers)

    for status in ["executed", "cancelled"]:
        for order in response[1][status]:
            sheet.append([
                order["folio"],
                order["product"]["name"],
                status,
                order["card_num"],
                order["amount"],
                order["created_at"].strftime("%Y-%m-%d %H:%M:%S") if order["created_at"] else "",
                order["assigned_user"]["name"],
                order["client_phone_number"],
                order["card_phone_number"],
                order["owner"]["name"],
                order["note"],
            ])

    # Save the workbook to a BytesIO stream
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=estadisticas.xlsx",
    }

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)