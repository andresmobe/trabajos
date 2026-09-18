"""CRUD de productos (MVC - Controller)."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.repositories import ProductRepository
from app.models.product import Product
from app.models.category import Category
from app.models.movement import StockMovement

products_bp  = Blueprint("products", __name__)
product_repo = ProductRepository()


@products_bp.route("/")
@login_required
def list_products():
    category_id = request.args.get("category", type=int)
    search_term = request.args.get("q", "").strip()

    uid = current_user.id
    if search_term:
        products = product_repo.search(search_term, user_id=uid)
    elif category_id:
        products = product_repo.get_by_category(category_id, user_id=uid)
    else:
        products = product_repo.get_active(user_id=uid)

    categories = Category.query.order_by(Category.name).all()
    return render_template(
        "products/list.html",
        products=products,
        categories=categories,
        selected_category=category_id,
        search_term=search_term,
    )


@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        errors = _validate_product_form(request.form)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("products/form.html", categories=categories, form=request.form)

        product = Product(
            name=request.form["name"].strip(),
            description=request.form.get("description", "").strip() or None,
            sku=request.form.get("sku", "").strip() or None,
            quantity=int(request.form["quantity"]),
            min_stock=int(request.form.get("min_stock", 5)),
            purchase_price=float(request.form["purchase_price"]),
            sale_price=float(request.form["sale_price"]),
            category_id=int(request.form["category_id"]) if request.form.get("category_id") else None,
            created_by=current_user.id,
        )
        product_repo.save(product)
        flash(f"Producto '{product.name}' creado exitosamente.", "success")
        return redirect(url_for("products.list_products"))

    return render_template("products/form.html", categories=categories, form={})


@products_bp.route("/<int:product_id>")
@login_required
def detail(product_id):
    product = product_repo.get_by_id(product_id)
    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("products.list_products"))

    movements = product.movements.order_by(StockMovement.created_at.desc()).limit(20).all()
    return render_template("products/detail.html", product=product, movements=movements)


@products_bp.route("/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product    = product_repo.get_by_id(product_id)
    categories = Category.query.order_by(Category.name).all()

    if not product:
        flash("Producto no encontrado.", "danger")
        return redirect(url_for("products.list_products"))

    if request.method == "POST":
        errors = _validate_product_form(request.form, editing=True)
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("products/form.html", product=product, categories=categories, form=request.form)

        product.name           = request.form["name"].strip()
        product.description    = request.form.get("description", "").strip() or None
        product.sku            = request.form.get("sku", "").strip() or None
        product.min_stock      = int(request.form.get("min_stock", 5))
        product.purchase_price = float(request.form["purchase_price"])
        product.sale_price     = float(request.form["sale_price"])
        product.category_id    = int(request.form["category_id"]) if request.form.get("category_id") else None
        product_repo.commit()

        flash(f"Producto '{product.name}' actualizado.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("products/form.html", product=product, categories=categories, form=product)


@products_bp.route("/<int:product_id>/delete", methods=["POST"])
@login_required
def delete_product(product_id):
    product = product_repo.get_by_id(product_id)
    if product:
        product.is_active = False
        product_repo.commit()
        flash(f"Producto '{product.name}' eliminado.", "info")
    return redirect(url_for("products.list_products"))


def _validate_product_form(form, editing=False) -> list:
    errors = []
    if not form.get("name", "").strip():
        errors.append("El nombre del producto es obligatorio.")
    try:
        if float(form.get("purchase_price", 0)) <= 0:
            errors.append("El precio de compra debe ser mayor a 0.")
    except (ValueError, TypeError):
        errors.append("Precio de compra invalido.")
    try:
        if float(form.get("sale_price", 0)) <= 0:
            errors.append("El precio de venta debe ser mayor a 0.")
    except (ValueError, TypeError):
        errors.append("Precio de venta invalido.")
    if not editing:
        try:
            if int(form.get("quantity", 0)) < 0:
                errors.append("La cantidad inicial no puede ser negativa.")
        except (ValueError, TypeError):
            errors.append("Cantidad invalida.")
    return errors
