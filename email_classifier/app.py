from flask import Flask, request, jsonify, render_template
from utils.file_reader import ler_arquivo
from utils.preprocess import preprocess_text
from dotenv import load_dotenv
import openai
import os

app = Flask(__name__)

# Carregar variáveis do .env
load_dotenv()

# Configure sua chave OpenAI
openai.api_key = os.getenv(API_key)

def classificar_e_responder(email_text):
    """
    Usa a OpenAI API para classificar o email e sugerir uma resposta.
    """
    prompt = f"""
Classifique o seguinte email como Produtivo ou Improdutivo e sugira uma resposta adequada:

Email: \"\"\"{email_text}\"\"\"

Responda no formato:
Categoria: <Produtivo/Improdutivo>
Resposta: <Texto da resposta>
"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    resposta_texto = response.choices[0].text.strip()
    # Separar categoria e resposta
    lines = resposta_texto.split("\n")
    categoria = lines[0].replace("Categoria:", "").strip()
    resposta = lines[1].replace("Resposta:", "").strip()
    return categoria, resposta

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/processar', methods=['POST'])
def processar_email():
    email_text = request.form.get('emailText', '')
    file = request.files.get('emailFile')

    if file:
        email_text = ler_arquivo(file)

    if not email_text:
        return jsonify({"erro": "Nenhum email fornecido"}), 400

    # Pré-processamento (limpeza básica)
    email_text = preprocess_text(email_text)

    # Classificação + Resposta
    categoria, resposta = classificar_e_responder(email_text)
    return jsonify({"categoria": categoria, "resposta": resposta})

if __name__ == '__main__':
    app.run(debug=True)
