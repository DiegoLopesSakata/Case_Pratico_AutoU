import os
from flask import Flask, request, render_template
from file_reader import read_file
from classifier import classify_email, gerar_resposta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    email_text = ""
    categoria = ""
    resposta = ""
    error = ""

    if request.method == "POST":
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            if file.filename.endswith(('.txt', '.pdf')):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                try:
                    file.save(filepath)
                    email_text = read_file(filepath)
                except Exception as e:
                    error = f"Erro ao ler arquivo: {str(e)}"
            else:
                error = "Formato de arquivo não suportado"

        elif "email_text" in request.form and request.form["email_text"].strip() != "":
            email_text = request.form["email_text"].strip()

        if email_text and not error:
            try:
                categoria = classify_email(email_text)
                resposta = gerar_resposta(categoria, email_text)
            except Exception as e:
                error = f"Erro ao processar email: {str(e)}"

    return render_template("index.html", 
                         email=email_text, 
                         categoria=categoria, 
                         resposta=resposta,
                         error=error)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)