from flask import Flask, send_from_directory, jsonify
import os
import re
import subprocess
import threading
import traceback

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_DIR = os.path.join("Hrrr", "static", "pngs")
PNG_DIR_REFC = os.path.join("Hrrr", "static", "REFC")
PNG_DIR_MSLP = os.path.join("Hrrr", "static", "MSLP")
PNG_DIR_TEMP2M = os.path.join("Hrrr", "static", "2mtemp")

@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "usa_leaflet.html")

@app.route("/reflectivity_images")
def get_pngs():
    # Find all REFC, MSLP, and 2mtemp PNGs by hour
    refc_files = [f for f in os.listdir(PNG_DIR_REFC) if re.match(r"REFC_(\d+)\.png$", f)]
    mslp_files = [f for f in os.listdir(PNG_DIR_MSLP) if re.match(r"MSLP_(\d+)\.png$", f)]
    temp2m_files = [f for f in os.listdir(PNG_DIR_TEMP2M) if re.match(r"2mtemp_(\d+)\.png$", f)]
    # Sort by hour
    refc_files.sort(key=lambda x: int(re.search(r"(\d+)", x).group()))
    mslp_files.sort(key=lambda x: int(re.search(r"(\d+)", x).group()))
    temp2m_files.sort(key=lambda x: int(re.search(r"(\d+)", x).group()))
    # Pair by hour (assume same number and order)
    result = []
    for refc, mslp, temp2m in zip(refc_files, mslp_files, temp2m_files):
        hour = int(re.search(r"(\d+)", refc).group())
        result.append({
            "hour": hour,
            "refc": f"/refc_pngs/{refc}",
            "mslp": f"/mslp_pngs/{mslp}",
            "temp2m": f"/temp2m_pngs/{temp2m}"
        })
    return jsonify(result)

@app.route("/refc_pngs/<path:filename>")
def serve_refc_png(filename):
    return send_from_directory(PNG_DIR_REFC, filename)

@app.route("/mslp_pngs/<path:filename>")
def serve_mslp_png(filename):
    return send_from_directory(PNG_DIR_MSLP, filename)

@app.route("/temp2m_pngs/<path:filename>")
def serve_temp2m_png(filename):
    return send_from_directory(PNG_DIR_TEMP2M, filename)

@app.route("/run-task")
def run_test_script():
    def run_test():
        try:
            subprocess.run(["python", "test.py"], check=True)
            print("test.py ran successfully!")
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            print(f"Error running test.py asynchronously:\n{error_trace}")

    def run_mslp():
        try:
            subprocess.run(["python", "mslp_script.py"], check=True)
            print("mslp_script.py ran successfully!")
        except subprocess.CalledProcessError as e:
            error_trace = traceback.format_exc()
            print(f"Error running mslp_script.py asynchronously:\n{error_trace}")

    threading.Thread(target=run_test).start()
    threading.Thread(target=run_mslp).start()
    return "test.py and mslp_script.py started in background!", 200

@app.route("/<path:filename>")
def serve_static_file(filename):
    return send_from_directory(BASE_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
