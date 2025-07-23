from .models import session, Order
import datetime
from sqlalchemy import func

def get_order_statistics(group_id: int):

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

    stats_dict = {}
    for row in results:
        month_key = row.month.strftime("%B")
        if month_key not in stats_dict:
            stats_dict[month_key] = {
                "month": month_key,
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

