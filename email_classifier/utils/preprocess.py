import re
import nltk
from nltk.corpus import stopwords

# Baixar stopwords caso ainda não tenha
nltk.download('stopwords')

def preprocess_text(text):
    """
    Limpa o texto do email:
    - Remove quebras de linha e espaços extras
    - Remove caracteres especiais
    - Remove stopwords
    """
    # Remover quebras de linha
    text = text.replace('\n', ' ')
    # Remover caracteres especiais
    text = re.sub(r'[^A-Za-z0-9À-ú ]+', '', text)
    # Converter para minúsculas
    text = text.lower()
    # Remover stopwords
    stop_words = set(stopwords.words('portuguese'))
    text_tokens = text.split()
    text_tokens = [word for word in text_tokens if word not in stop_words]
    return ' '.join(text_tokens)
