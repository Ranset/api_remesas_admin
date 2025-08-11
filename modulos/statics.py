from .models import session, Order
import datetime
from sqlalchemy import func

def get_order_statistics(group_id: int):
    from .date_utility import DateUtlility

    now = datetime.datetime.now()
    three_months_ago = now - datetime.timedelta(days=90)

    results = (
        session.query(
            func.date_trunc('month', Order.created_at).label('month'),
            Order.status,
            func.count(Order.id).label('orders_count'),
            func.sum(Order.amount).label('total_amount')
        )
        .filter(
            Order.created_at >= three_months_ago,
            Order.status.in_(["executed", "cancelled"]),
            Order.group_id.in_([str(group_id)])
        )
        .group_by(func.date_trunc('month', Order.created_at), Order.status)
        .order_by(func.date_trunc('month', Order.created_at).desc())
        .all()
    )

    translate = DateUtlility()

    stats_dict = {}
    for row in results:
        month_key = row.month.strftime("%B")
        if month_key not in stats_dict:
            stats_dict[month_key] = {
                "month": translate.translate_month(month_key),
                "executed": {"orders_count": 0, "total_amount": 0},
                "cancelled": {"orders_count": 0, "total_amount": 0}
            }
        stats_dict[month_key][row.status] = {
            "orders_count": row.orders_count,
            "total_amount": float(row.total_amount) if row.total_amount else 0
        }

    session.close()
    # Devuelve una lista de diccionarios, uno por mes
    static = list(stats_dict.values())

    message = [True, static]

    return message


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
        "Estado", "Número tarjeta", "Product ID", "Cantidad", "Fecha de creación",
        "Assigned User ID", "Folio", "Teléfono Cliente", "Teléfono Tarjeta",
        "Nota", "Owner ID"
    ]
    sheet.append(headers)

    for status in ["executed", "cancelled"]:
        for order in response[1][status]:
            sheet.append([
                status,
                order["card_num"],
                f'{order["product"]["id"]} - {order["product"]["name"]}',
                order["amount"],
                order["created_at"].strftime("%Y-%m-%d %H:%M:%S") if order["created_at"] else "",
                f'{order["assigned_user"]["id"]} - {order["assigned_user"]["name"]}',
                order["folio"],
                order["client_phone_number"],
                order["card_phone_number"],
                order["note"],
                f'{order["owner"]["id"]} - {order["owner"]["name"]}'
            ])

    # Save the workbook to a BytesIO stream
    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=estadisticas.xlsx",
    }

    return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)