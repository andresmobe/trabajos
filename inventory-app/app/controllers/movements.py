"""
Controlador de movimientos de inventario (entradas y salidas).
Usa InventoryService para aplicar la logica de negocio.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.repositories import ProductRepository, MovementRepository
from app.services import InventoryService
from app.models.category import Category

movements_bp  = Blueprint("movements", __name__)
product_repo  = ProductRepository()
movement_repo = MovementRepository()
inv_service   = InventoryService()


@movements_bp.route("/")
@login_required
def list_movements():
    days      = request.args.get("days", 30, type=int)
    movements = movement_repo.get_recent(days=days, user_id=current_user.id)
    return render_template("movements/list.html", movements=movements, days=days)


@movements_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_movement():
    products   = product_repo.get_active(user_id=current_user.id)
    categories = Category.query.order_by(Category.name).all()

    # Precarga de producto desde querystring (desde detalle de producto)
    preselected_id = request.args.get("product_id", type=int)

    if request.method == "POST":
        product_id    = request.form.get("product_id", type=int)
        movement_type = request.form.get("movement_type", "")
        quantity      = request.form.get("quantity", 0, type=int)
        unit_price    = request.form.get("unit_price", None)
        notes         = request.form.get("notes", "").strip() or None

        product = product_repo.get_by_id(product_id) if product_id else None
        if not product:
            flash("Selecciona un producto valido.", "danger")
            return render_template("movements/form.html", products=products, categories=categories)

        if movement_type not in ("entry", "exit"):
            flash("Tipo de movimiento invalido.", "danger")
            return render_template("movements/form.html", products=products, categories=categories)

        try:
            unit_price_val = float(unit_price) if unit_price else None
            inv_service.register_movement(
                product=product,
                user_id=current_user.id,
                movement_type=movement_type,
                quantity=quantity,
                unit_price=unit_price_val,
                notes=notes,
            )
            action = "Entrada" if movement_type == "entry" else "Salida"
            flash(f"{action} de {quantity} unidades registrada para '{product.name}'.", "success")
            return redirect(url_for("movements.list_movements"))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "movements/form.html",
        products=products,
        categories=categories,
        preselected_id=preselected_id,
    )
