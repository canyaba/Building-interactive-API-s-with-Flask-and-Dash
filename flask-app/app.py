from flask import Flask, request, jsonify, send_file
from PIL import Image
from io import BytesIO
from pathlib import Path
import json
import os

from fitness_influencer_mcp.workout_plan_generator import WorkoutPlanGenerator

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(exist_ok=True)

ALLOWED_OUTPUT_TYPES = ["PNG", "JPEG", "BMP", "GIF", "TIFF", "WEBP"]


@app.route("/")
def index():
    return """
    <h1>Flask Utility App</h1>
    <p>This app provides two main routes:</p>

    <h2>1. POST /convert</h2>
    <p>Convert an uploaded image to another format using Pillow.</p>
    <p><strong>Form fields:</strong></p>
    <ul>
        <li><strong>image</strong> - the uploaded image file</li>
        <li><strong>output_type</strong> - desired format</li>
    </ul>
    <p><strong>Available output types:</strong> PNG, JPEG, BMP, GIF, TIFF, WEBP</p>

    <h2>2. POST /generate-workout-plan</h2>
    <p>Generate a workout plan using the fitness-influencer-mcp package.</p>
    <p><strong>JSON body:</strong></p>
    <pre>
{
  "goal": "muscle gain",
  "experience": "beginner",
  "days_per_week": 4,
  "equipment": "full_gym"
}
    </pre>
    """


@app.route("/convert", methods=["POST"])
def convert():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    output_type = request.form.get("output_type", "").upper()

    if output_type not in ALLOWED_OUTPUT_TYPES:
        return jsonify({
            "error": "Invalid output type.",
            "allowed_output_types": ALLOWED_OUTPUT_TYPES
        }), 400

    image_file = request.files["image"]

    try:
        image = Image.open(image_file)

        if output_type == "JPEG":
            image = image.convert("RGB")

        output_buffer = BytesIO()
        image.save(output_buffer, format=output_type)
        output_buffer.seek(0)

        original_name = Path(image_file.filename).stem
        download_name = f"{original_name}.{output_type.lower()}"

        mimetype = "image/jpeg" if output_type == "JPEG" else f"image/{output_type.lower()}"

        return send_file(
            output_buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/generate-workout-plan", methods=["POST"])
def generate_workout_plan():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    required_fields = ["goal", "experience", "days_per_week", "equipment"]
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({
            "error": "Missing required fields.",
            "missing_fields": missing_fields
        }), 400

    goal = data["goal"]
    experience = data["experience"]
    days_per_week = data["days_per_week"]
    equipment = data["equipment"]

    try:
        generator = WorkoutPlanGenerator()

        plan = generator.generate_plan(
            goal=goal,
            experience=experience,
            days_per_week=days_per_week,
            equipment=equipment
        )

        safe_filename = f"workout_{goal}_{experience}_{days_per_week}days".replace(" ", "_").lower()
        md_path = generator.export_markdown(plan, safe_filename)
        json_path = generator.export_json(plan, safe_filename)

        return jsonify({
            "message": "Workout plan generated successfully.",
            "input": {
                "goal": goal,
                "experience": experience,
                "days_per_week": days_per_week,
                "equipment": equipment
            },
            "plan": plan,
            "exports": {
                "markdown_file": str(md_path),
                "json_file": str(json_path)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)