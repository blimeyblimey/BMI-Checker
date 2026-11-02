import logging
from flask import Blueprint, render_template, request, jsonify, send_file
from app.services.health_service import HealthService
from app.services.pdf_service import PDFService

bp = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/api/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json() or {}
        result = HealthService.calculate_bmi(
            data.get("weight"),
            data.get("weight_unit", "kg"),
            data.get("height"),
            data.get("height_unit", "cm"),
            data.get("age")
        )
        return jsonify({"success": True, "data": result})
    except ValueError as ve:
        logger.warning(f"Validation error during BMI calculation: {ve}")
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in calculate route: {e}", exc_info=True)
        return jsonify({"success": False, "message": "An internal error occurred."}), 500

@bp.route("/api/assess-health", methods=["POST"])
def assess_health():
    try:
        data = request.get_json() or {}
        answers = data.get("answers", [])
        result, advice = HealthService.evaluate_health(answers)
        return jsonify({
            "success": True,
            "data": {"health_result": result, "health_advice": advice}
        })
    except Exception as e:
        logger.error(f"Error in health assessment: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to process health assessment."}), 500

@bp.route("/api/export-pdf", methods=["POST"])
def export_pdf():
    try:
        data = request.get_json() or {}
        buffer, filename = PDFService.generate_report(data)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Failed to generate PDF."}), 500