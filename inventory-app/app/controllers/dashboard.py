"""Dashboard principal (MVC - Controller)."""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app.repositories import ProductRepository, MovementRepository
from app.models.alert import StockAlert
from app.models.product import Product
from app.extensions import db

dashboard_bp = Blueprint("dashboard", __name__)
product_repo  = ProductRepository()
movement_repo = MovementRepository()


@dashboard_bp.route("/")
@login_required
def index():
    uid = current_user.id

    all_products     = product_repo.get_active(user_id=uid)
    low_stock        = product_repo.get_low_stock(user_id=uid)
    recent_movements = movement_repo.get_recent(days=7, user_id=uid)

    # Alertas solo de productos del usuario actual
    unread_alerts = (
        StockAlert.query
        .join(Product, Product.id == StockAlert.product_id)
        .filter(Product.created_by == uid, StockAlert.is_read == False)
        .count()
    )

    total_value = sum(
        float(p.quantity) * float(p.purchase_price) for p in all_products
    )

    today = datetime.utcnow().date()
    chart_labels  = []
    chart_entries = []
    chart_exits   = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime("%d/%m"))
        chart_entries.append(sum(
            m.quantity for m in recent_movements
            if m.created_at.date() == day and m.movement_type == "entry"
        ))
        chart_exits.append(sum(
            m.quantity for m in recent_movements
            if m.created_at.date() == day and m.movement_type == "exit"
        ))

    return render_template(
        "dashboard/index.html",
        total_products=len(all_products),
        low_stock_count=len(low_stock),
        low_stock_products=low_stock[:5],
        recent_movements=recent_movements[:10],
        total_value=total_value,
        unread_alerts=unread_alerts,
        chart_labels=chart_labels,
        chart_entries=chart_entries,
        chart_exits=chart_exits,
    )


@dashboard_bp.route("/api/alerts")
@login_required
def api_alerts():
    uid = current_user.id
    alerts = (
        StockAlert.query
        .join(Product, Product.id == StockAlert.product_id)
        .filter(Product.created_by == uid, StockAlert.is_read == False)
        .order_by(StockAlert.created_at.desc())
        .limit(10)
        .all()
    )
    data = [
        {
            "id": a.id,
            "product": a.product.name if a.product else "–",
            "quantity": a.quantity,
            "min_stock": a.min_stock,
            "created_at": a.created_at.strftime("%d/%m %H:%M"),
        }
        for a in alerts
    ]
    return jsonify({"count": len(data), "alerts": data})


@dashboard_bp.route("/api/alerts/<int:alert_id>/read", methods=["POST"])
@login_required
def mark_alert_read(alert_id):
    alert = StockAlert.query.get_or_404(alert_id)
    alert.is_read = True
    db.session.commit()
    return jsonify({"ok": True})


@dashboard_bp.route("/api/alerts/read-all", methods=["POST"])
@login_required
def mark_all_read():
    uid = current_user.id
    (
        StockAlert.query
        .join(Product, Product.id == StockAlert.product_id)
        .filter(Product.created_by == uid, StockAlert.is_read == False)
        .update({"is_read": True}, synchronize_session="fetch")
    )
    db.session.commit()
    return jsonify({"ok": True})
