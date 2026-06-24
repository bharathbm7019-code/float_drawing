from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
from blender_config import get_blender_path, get_output_folder
from script_generator import generate_blender_script
import subprocess
import os
import tempfile

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    try:
        dimensions    = request.get_json()
        print(f"Received dimensions: {dimensions}")
        blender_path  = get_blender_path()
        output_folder = get_output_folder()
        script_code   = generate_blender_script(dimensions, output_folder)

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp:
            tmp.write(script_code)
            script_path = tmp.name

        print(f"Script saved to: {script_path}")
        print(f"Running Blender from: {blender_path}")

        result = subprocess.run(
            [blender_path, "--background", "--python", script_path],
            capture_output=True, text=True, timeout=300
        )

        print("=" * 60)
        print("BLENDER STDOUT:"); print(result.stdout)
        print("BLENDER STDERR:"); print(result.stderr)
        print("Return code:", result.returncode)

        obj_path = os.path.join(output_folder, "model.obj")
        png_path = os.path.join(output_folder, "render.png")

        files_ready = {
            "obj": os.path.exists(obj_path),
            "png": os.path.exists(png_path),
        }

        if not files_ready["obj"]:
            return jsonify({
                "success": False,
                "error": "Blender ran but no output files were created.",
                "blender_log": result.stdout[-1000:]
            }), 500

        return jsonify({
            "success": True,
            "files": files_ready,
            "message": "Files generated successfully!"
        })

    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Blender timed out."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/generate-drawing", methods=["POST"])
def generate_drawing():
    try:
        from drawing_generator import generate_drawing_pdf
        dimensions    = request.get_json()
        output_folder = get_output_folder()
        pdf_path      = os.path.join(output_folder, "drawing.pdf")
        generate_drawing_pdf(dimensions, pdf_path)
        return jsonify({"success": True, "message": "Drawing generated!"})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/download/<filetype>")
def download(filetype):
    output_folder = get_output_folder()
    file_map = {
        "obj": os.path.join(output_folder, "model.obj"),
        "png": os.path.join(output_folder, "render.png"),
        "pdf": os.path.join(output_folder, "drawing.pdf"),
    }
    if filetype not in file_map:
        return "Invalid file type", 400
    filepath = file_map[filetype]
    if not os.path.exists(filepath):
        return "File not found — please generate first", 404
    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    print("Starting FloatSwitch Automation Server...")
    print("Open your browser at: http://localhost:5000")
    app.run(debug=True, port=5000)