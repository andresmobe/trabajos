"""CRUD de categorias de productos."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.category import Category

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/")
@login_required
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return render_template("categories/list.html", categories=categories)


@categories_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_category():
    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None

        if not name:
            flash("El nombre de la categoria es obligatorio.", "danger")
            return render_template("categories/form.html")

        if Category.query.filter_by(name=name).first():
            flash("Ya existe una categoria con ese nombre.", "danger")
            return render_template("categories/form.html", form=request.form)

        cat = Category(name=name, description=description)
        db.session.add(cat)
        db.session.commit()
        flash(f"Categoria '{name}' creada.", "success")
        return redirect(url_for("categories.list_categories"))

    return render_template("categories/form.html", form={})


@categories_bp.route("/<int:cat_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(cat_id):
    cat = Category.query.get_or_404(cat_id)

    if request.method == "POST":
        name        = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None

        if not name:
            flash("El nombre es obligatorio.", "danger")
            return render_template("categories/form.html", category=cat, form=request.form)

        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != cat.id:
            flash("Ya existe una categoria con ese nombre.", "danger")
            return render_template("categories/form.html", category=cat, form=request.form)

        cat.name        = name
        cat.description = description
        db.session.commit()
        flash(f"Categoria '{name}' actualizada.", "success")
        return redirect(url_for("categories.list_categories"))

    return render_template("categories/form.html", category=cat, form=cat)


@categories_bp.route("/<int:cat_id>/delete", methods=["POST"])
@login_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    if cat.products.count() > 0:
        flash("No se puede eliminar una categoria con productos asociados.", "warning")
    else:
        db.session.delete(cat)
        db.session.commit()
        flash(f"Categoria '{cat.name}' eliminada.", "info")
    return redirect(url_for("categories.list_categories"))
