from flask import Flask, send_from_directory, jsonify
import os
import re

app = Flask(__name__)

PNG_DIR = os.path.join("Hrrr", "static", "pngs")  # Updated path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "usa_leaflet.html")

@app.route("/reflectivity_images")
def reflectivity_images():
    # Find all PNGs matching the pattern and sort by hour number
    files = [
        f for f in os.listdir(PNG_DIR)
        if re.match(r"reflectivity_(\d+)\.png$", f)
    ]
    # Sort by the integer hour in the filename
    files.sort(key=lambda x: int(re.search(r"reflectivity_(\d+)\.png$", x).group(1)))
    png_urls = [f"/pngs/{fname}" for fname in files]
    return jsonify(png_urls)

@app.route("/pngs/<path:filename>")
def serve_png(filename):
    return send_from_directory(PNG_DIR, filename)

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
