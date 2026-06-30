import os
import time
from pathlib import Path

from flask import Flask, flash, redirect, render_template, request, send_from_directory, url_for
import fitz  # PyMuPDF

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
ALLOWED_EXTENSIONS = {"pdf"}

app = Flask(__name__)
app.secret_key = "mexit-pdf-extractor"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50 MB limit


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        pages.append(f"--- Page {i} ---\n{text}")
    doc.close()
    return "\n".join(pages)


def list_outputs() -> list[dict]:
    output_dir = Path(OUTPUT_FOLDER)
    files = []
    for f in sorted(output_dir.glob("*.txt"), key=lambda p: p.stat().st_mtime, reverse=True):
        files.append({
            "name": f.name,
            "size": f.stat().st_size,
            "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f.stat().st_mtime)),
        })
    return files


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.", "error")
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            flash("No file selected.", "error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Only PDF files are supported.", "error")
            return redirect(request.url)

        original_stem = Path(file.filename).stem
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        safe_stem = "".join(c if c.isalnum() or c in "-_" else "_" for c in original_stem)
        upload_path = os.path.join(UPLOAD_FOLDER, f"{safe_stem}_{timestamp}.pdf")
        output_filename = f"{safe_stem}_{timestamp}.txt"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        file.save(upload_path)

        try:
            text = extract_text(upload_path)
            Path(output_path).write_text(text, encoding="utf-8")
        except Exception as e:
            flash(f"Extraction failed: {e}", "error")
            return redirect(url_for("index"))

        flash(f"Extracted text saved as {output_filename}", "success")
        return redirect(url_for("index"))

    return render_template("index.html", outputs=list_outputs())


@app.route("/output/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


@app.route("/output/<filename>/view")
def view(filename):
    filepath = Path(OUTPUT_FOLDER) / filename
    if not filepath.exists():
        flash("File not found.", "error")
        return redirect(url_for("index"))
    content = filepath.read_text(encoding="utf-8")
    return render_template("view.html", filename=filename, content=content)


if __name__ == "__main__":
    Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
    Path(OUTPUT_FOLDER).mkdir(exist_ok=True)
    app.run(debug=True, port=5000)
