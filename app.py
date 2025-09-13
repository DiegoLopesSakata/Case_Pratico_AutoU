import os
from flask import Flask, request, render_template
from email_classifier.file_reader import read_file
from email_classifier.classifier import classify_email, gerar_resposta

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email_text = ""

        # Caso 1: upload de arquivo
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            email_text = read_file(filepath)

        # Caso 2: texto inserido diretamente
        elif "email_text" in request.form and request.form["email_text"].strip() != "":
            email_text = request.form["email_text"]

        if email_text:
            categoria = classify_email(email_text)
            resposta = gerar_resposta(categoria)
            return render_template("index.html", email=email_text, categoria=categoria, resposta=resposta)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
