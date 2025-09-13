import PyPDF2

def ler_arquivo(file):
    """
    Lê arquivos .txt ou .pdf e retorna o texto.
    """
    if file.filename.endswith('.txt'):
        return file.read().decode('utf-8')
    elif file.filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text()
        return texto
    return ""