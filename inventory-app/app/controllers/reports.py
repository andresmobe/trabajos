"""
Controlador de reportes.
Usa ReportFactory (Factory Method) para crear el reporte solicitado.
"""
import csv
import io
from flask import Blueprint, render_template, request, Response, jsonify
from flask_login import login_required, current_user
from app.factories import ReportFactory

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/")
@login_required
def index():
    report_type = request.args.get("type", "movements")
    days        = request.args.get("days", 30, type=int)
    fmt         = request.args.get("fmt", "html")

    try:
        report  = ReportFactory.create(report_type)
        data    = report.generate(days=days, user_id=current_user.id)
    except ValueError as exc:
        data = {"title": "Error", "error": str(exc), "data": []}

    if fmt == "json":
        # Estrategia JSON
        safe_data = _make_serializable(data)
        return jsonify(safe_data)

    if fmt == "csv":
        # Estrategia CSV
        return _export_csv(report_type, data)

    # Estrategia HTML (default)
    return render_template(
        "reports/index.html",
        report_data=data,
        report_type=report_type,
        days=days,
        available_types=ReportFactory.available_types(),
    )


def _export_csv(report_type: str, data: dict) -> Response:
    """Estrategia de exportacion CSV (Strategy pattern aplicado a exportacion)."""
    output = io.StringIO()
    writer = csv.writer(output)

    rows = data.get("data", [])
    if not rows:
        writer.writerow(["Sin datos"])
    elif report_type == "movements" and rows:
        writer.writerow(["Fecha", "Producto", "Tipo", "Cantidad", "Stock Antes", "Stock Despues", "Precio Unit.", "Notas"])
        for m in rows:
            writer.writerow([
                m.created_at.strftime("%Y-%m-%d %H:%M"),
                m.product.name if m.product else "",
                "Entrada" if m.movement_type == "entry" else "Salida",
                m.quantity,
                m.quantity_before,
                m.quantity_after,
                m.unit_price or "",
                m.notes or "",
            ])
    elif report_type == "popular":
        writer.writerow(["Producto", "Total Vendido"])
        for row in rows:
            writer.writerow([row["name"], row["total_sold"]])
    elif report_type == "low_stock":
        writer.writerow(["Producto", "SKU", "Stock Actual", "Stock Minimo", "Categoria"])
        for p in rows:
            writer.writerow([
                p.name,
                p.sku or "",
                p.quantity,
                p.min_stock,
                p.category.name if p.category else "",
            ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=reporte_{report_type}.csv"},
    )


def _make_serializable(data: dict) -> dict:
    """Convierte objetos SQLAlchemy a dict para respuesta JSON."""
    result = {"title": data.get("title", ""), "days": data.get("days"), "total": data.get("total")}
    rows = data.get("data", [])
    if rows and hasattr(rows[0], "__tablename__"):
        # Son objetos del ORM
        serialized = []
        for obj in rows:
            if hasattr(obj, "movement_type"):
                serialized.append({
                    "id": obj.id,
                    "product": obj.product.name if obj.product else "",
                    "type": obj.movement_type,
                    "quantity": obj.quantity,
                    "created_at": obj.created_at.isoformat(),
                })
            else:
                serialized.append({"name": obj.name, "quantity": obj.quantity, "min_stock": obj.min_stock})
        result["data"] = serialized
    else:
        result["data"] = rows
    return result
