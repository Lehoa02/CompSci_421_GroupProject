# app.py
from flask import Flask, jsonify, render_template, request
import csv
from pathlib import Path
from tasks import compute_dft_features  # Celery task

app = Flask(__name__)

CSV_PATH = Path("dft_features.csv")
UPLOAD_FOLDER = Path("data/audio")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def load_features():
    if not CSV_PATH.exists():
        return []

    rows = []
    with CSV_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["sr"] = int(row["sr"])
            row["spectral_centroid_mean"] = float(row["spectral_centroid_mean"])
            row["spectral_bandwidth_mean"] = float(row["spectral_bandwidth_mean"])
            row["rms_mean"] = float(row["rms_mean"])
            rows.append(row)
    return rows


def save_features(rows):
    fieldnames = ["file_path", "sr", "spectral_centroid_mean",
                  "spectral_bandwidth_mean", "rms_mean"]
    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@app.route("/api/features")
def api_features():
    return jsonify(load_features())


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    """
    Upload an audio file, analyze it via Celery, update CSV,
    and return the computed features.
    """
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"error": "No file provided"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in {".wav", ".mp3", ".flac", ".ogg"}:
        return jsonify({"error": "Unsupported file type"}), 400

    # Save file into data/audio
    filename = Path(file.filename).name
    save_path = UPLOAD_FOLDER / filename
    file.save(save_path)

    # Send to Celery worker
    async_result = compute_dft_features.delay(str(save_path))
    try:
        features = async_result.get(timeout=300)  # wait for worker
    except Exception as e:
        return jsonify({"error": f"Processing failed: {e}"}), 500

    # --- FIX: de-duplicate by file_path before saving ---
    rows = load_features()
    rows = [r for r in rows if r["file_path"] != features["file_path"]]
    rows.append(features)
    save_features(rows)
    # ---------------------------------------------------

    return jsonify(features)
''' Old version
    # Update CSV with this new row (append in-memory, then rewrite)
    rows = load_features()
    rows.append(features)
    save_features(rows)

    return jsonify(features)'''


if __name__ == "__main__":
    app.run(debug=True)
