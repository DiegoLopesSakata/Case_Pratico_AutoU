from transformers import pipeline

# Criar pipeline de classificação zero-shot
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Labels personalizadas
LABELS = ["Produtivo", "Improdutivo"]

def classify_email(texto: str) -> str:
    """Classifica o email como Produtivo ou Improdutivo"""
    resultado = classifier(texto, candidate_labels=LABELS)
    categoria = resultado["labels"][0]  # pega a label com maior score
    return categoria

def gerar_resposta(categoria: str) -> str:
    """Sugere uma resposta automática"""
    if categoria == "Produtivo":
        return "Obrigado pelo seu contato. Sua solicitação foi registrada e nossa equipe retornará em breve."
    else:
        return "Agradecemos sua mensagem!"
