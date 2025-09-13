import pdfplumber

def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def read_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def read_file(file_path: str) -> str:
    if file_path.endswith(".txt"):
        return read_txt(file_path)
    elif file_path.endswith(".pdf"):
        return read_pdf(file_path)
    else:
        raise ValueError("Formato de arquivo não suportado. Use .txt ou .pdf")
