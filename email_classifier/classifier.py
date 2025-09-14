from transformers import pipeline
import nltk
from nltk.corpus import stopwords
import re
import requests
import json
import os
from dotenv import load_dotenv
import random
from datetime import datetime
import openai  # ✅ OpenAI mais estável

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializações
nltk.download('stopwords')
stop_words = set(stopwords.words('portuguese'))

# Pipeline de classificação
classifier = pipeline("zero-shot-classification", 
                     model="MoritzLaurer/deberta-v3-base-zeroshot-v2.0")

# Categorias para classificação
LABELS = [
    "solicitação de suporte técnico, problema urgente, erro no sistema, ausência, problema de saúde, emergência, ajuda necessária",
    "mensagem de cumprimento, felicitações, agradecimentos, desejos, parabéns, reconhecimento, elogios"
]

# Configuração da OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Configurar OpenAI se a chave existir
if OPENAI_API_KEY and OPENAI_API_KEY != 'sua_chave_openai_aqui':
    openai.api_key = OPENAI_API_KEY
    print("✅ OpenAI configurada")
else:
    print("⚠️  OpenAI não configurada - usando fallback")

def preprocess_text(texto: str) -> str:
    """Pré-processamento do texto"""
    texto = texto.lower()
    texto = re.sub(r'[^a-záàâãéèêíïóôõöúçñ\s]', ' ', texto)
    palavras = [p for p in texto.split() if p not in stop_words and len(p) > 2]
    return " ".join(palavras)

def classify_email(texto: str) -> str:
    """Classificação do email com contexto melhorado"""
    texto_prep = preprocess_text(texto)
    prompt = f"Classifique este email considerando o contexto completo: {texto_prep}"
    
    resultado = classifier(prompt, candidate_labels=LABELS)
    
    # Verificar confiança
    if resultado["scores"][0] > 0.6:
        if any(keyword in resultado["labels"][0] for keyword in ["solicitação", "problema", "urgente", "ausência", "saúde", "emergência", "ajuda"]):
            return "Produtivo"
        else:
            return "Improdutivo"
    else:
        # Fallback por palavras-chave com contexto melhorado
        # PRIORIDADE: Verificar primeiro se é sobre saúde/ausência
        palavras_saude = [
            'indisgestão', 'enjoo', 'náusea', 'mal estar', 'febre', 'gripe', 'resfriado', 
            'temperatura', 'dor', 'doente', 'saúde', 'médico', 'hospital', 'indisposição',
            'ausente', 'ausência', 'licença', 'atestado', 'consulta', 'recuperação',
            'medicamento', 'remédio', 'sintoma', 'vômito', 'diarréia', 'diarreia', 'passando mal'
        ]
        
        palavras_produtivo = [
            'problema', 'erro', 'travou', 'urgente', 'ajuda', 'suporte', 'sistema', 
            'relatório', 'não consigo', 'emergência', 'falha', 'bug', 'comparecer', 
            'reunião', 'entregar', 'preciso', 'necessito', 'importante', 'prioridade', 
            'filho', 'filha', 'filhos', 'familia', 'familiar', 'lento', 'congelou', 
            'offline', 'quebrado', 'defeito', 'não funciona', 'servidor', 'offline'
        ]
        
        palavras_improdutivo = [
            'feliz', 'natal', 'ano novo', 'parabéns', 'obrigado', 'agradeço', 
            'desejo', 'cumprimentos', 'agradecimento', 'comemoração', 'festas',
            'apoio', 'melhor', 'agradecer', 'reconhecimento', 'bom dia', 'boa tarde', 
            'boa noite', 'elogio', 'excelente', 'fantástico', 'incrível', 'maravilhoso', 
            'ótimo', 'perfeito', 'adorei', 'amei'
        ]
        
        texto_lower = texto.lower()
        
        # PRIMEIRO verificar se é sobre saúde/ausência (prioridade máxima)
        saude_count = sum(1 for p in palavras_saude if p in texto_lower)
        if saude_count > 0:
            return "Produtivo"
        
        # Depois verificar outros tipos produtivos
        produtivo_count = sum(1 for p in palavras_produtivo if p in texto_lower)
        improdutivo_count = sum(1 for p in palavras_improdutivo if p in texto_lower)
        
        # Se for claro, retornar a categoria com mais ocorrências
        if produtivo_count > improdutivo_count:
            return "Produtivo"
        elif improdutivo_count > produtivo_count:
            return "Improdutivo"
        else:
            # Se empate, analisar contexto mais profundamente
            if any(ctx in texto_lower for ctx in ['preciso', 'necessito', 'urgente', 'problema', 'ajuda', 'ausent']):
                return "Produtivo"
            else:
                return "Improdutivo"

def gerar_resposta(categoria: str, email_texto: str) -> str:
    """Geração de resposta usando IA real"""
    
    # Tentar OpenAI primeiro (mais confiável)
    if OPENAI_API_KEY and OPENAI_API_KEY != 'sua_chave_openai_aqui':
        try:
            resposta = gerar_resposta_openai(categoria, email_texto)
            if resposta and len(resposta) > 10:
                print("✅ Resposta gerada por OpenAI")
                return resposta
        except Exception as e:
            print(f"❌ Erro OpenAI: {e}")
    
    # Usar fallback inteligente
    print("🎯 Usando sistema de fallback inteligente")
    return gerar_resposta_avancada(categoria, email_texto)

def gerar_resposta_openai(categoria: str, email_texto: str) -> str:
    """Geração de resposta usando OpenAI API"""
    try:
        prompt = f"""
        Gere uma resposta profissional em português do Brasil para um email classificado como {categoria}.
        Seja empático, adequado ao contexto e mantenha um tom profissional.
        
        Email recebido:
        "{email_texto[:400]}"
        
        Resposta:
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente profissional que responde emails corporativos em português."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        resposta = response.choices[0].message.content.strip()
        return resposta
        
    except Exception as e:
        raise Exception(f"OpenAI error: {str(e)}")

def gerar_resposta_avancada(categoria: str, email_texto: str) -> str:
    """Sistema de fallback super-avançado com múltiplas variações"""
    
    email_lower = email_texto.lower()
    hora_atual = datetime.now().hour
    saudacao = "Bom dia" if 5 <= hora_atual < 12 else "Boa tarde" if 12 <= hora_atual < 18 else "Boa noite"
    
    # Diferentes variações de respostas para cada cenário
    respostas = {
        "Produtivo": {
            "saude": [
                f"{saudacao}, entendemos que você não está se sentindo bem. A saúde sempre vem em primeiro lugar! Por favor, descanse e cuide-se. Mantenha-nos informado sobre sua recuperação e retorne quando estiver melhor. Desejamos rápida recuperação!",
                f"{saudacao}, compreendemos perfeitamente sua situação de saúde. Sua recuperação é o mais importante agora. Fique tranquilo(a) e priorize seu bem-estar. Estaremos aqui quando você voltar. Melhoras!",
                f"{saudacao}, agradecemos por nos informar sobre seu estado de saúde. Por favor, descanse e se recupere completamente. Não se preocupe com nada aqui - sua saúde é prioridade total. Desejamos melhoras!"
            ],
            "familia": [
                f"{saudacao}, entendemos completamente que situações familiares exigem nossa atenção imediata. Por favor, cuide de sua família que nós cuidamos de tudo aqui. Retorne quando a situação estiver resolvida. Força!",
                f"{saudacao}, família sempre em primeiro lugar! Compreendemos sua necessidade de ausência e apoiamos totalmente sua decisão. Cuide de seus entes queridos e retorne quando possível. Estamos na torcida!",
                f"{saudacao}, situações familiares são realmente prioritárias. Fique tranquilo(a) para resolver tudo o que for necessário. Estaremos aqui dando suporte no que precisar. Conte conosco!"
            ],
            "tecnico": [
                f"{saudacao}, agradecemos pelo relato do problema técnico. Nossa equipe especializada já foi acionada e está trabalhando ativamente na solução. Retornaremos em até 1 hora com atualizações. Obrigado pela paciência!",
                f"{saudacao}, identificamos o problema técnico relatado. Nossos engenheiros já estão investigando a causa raiz e implementando a solução. Você receberá uma atualização em breve. Agradecemos sua compreensão!",
                f"{saudacao}, problema técnico registrado com sucesso! Nossa equipe de TI está analisando e corrigindo a falha. Previsão de normalização em até 2 horas. Obrigado por reportar!"
            ],
            "urgente": [
                f"{saudacao}, reconhecemos a urgência da situação! Este caso está sendo tratado com PRIORIDADE MÁXIMA. Toda nossa equipe está focada na resolução. Retornaremos em até 30 minutos. Obrigado!",
                f"{saudacao}, entendemos a criticalidade do assunto! Ativamos nosso protocolo de emergência e alocamos todos os recursos necessários. Solução em andamento - retorno em breve!",
                f"{saudacao}, situação de urgência identificada! Mobilizamos nossa equipe integral para resolver isso o mais rápido possível. Você será o primeiro a saber assim que resolvido."
            ],
            "geral": [
                f"{saudacao}, agradecemos seu contato! Sua solicitação foi recebida e está sendo analisada por nossa equipe especializada. Retornaremos com uma solução em até 2 horas úteis. Obrigado!",
                f"{saudacao}, recebemos sua mensagem! Nossos analistas já estão trabalhando na sua demanda e em breve teremos uma resposta completa. Agradecemos sua confiança!",
                f"{saudacao}, obrigado por entrar em contato! Sua requisição foi registrada e está em processamento. Retornaremos com novidades o mais breve possível."
            ]
        },
        "Improdutivo": {
            "natal": [
                f"{saudacao}, que mensagem maravilhosa! Agradecemos de coração seus sinceros desejos natalinos. Que esta época mágica traga muita luz, amor e prosperidade para você e todos os seus. Feliz Natal e um Ano Novo repleto de conquistas! 🎄🌟",
                f"{saudacao}, obrigado por seus calorosos votos! Que o espírito do Natal ilumine seu coração e que o novo ano traga realizações extraordinárias. Feliz Natal e Próspero Ano Novo para você e família! ✨",
                f"{saudacao}, que alegria receber seus desejos natalinos! Que esta seja uma época de renovação e que 2024 seja repleto de saúde, paz e sucesso. Felicidades a você e todos os seus!"
            ],
            "parabens": [
                f"{saudacao}, ficamos extremamente honrados e felizes com seu reconhecimento! Feedback como o seu é o combustível que nos motiva a sempre dar o nosso melhor. Muito obrigado pela confiança! 🎉",
                f"{saudacao}, que elogio incrível! Suas palavras aqueceram nosso coração e reforçam nosso compromisso com a excelência. É um prazer imenso poder atendê-lo! Obrigado! 🌟",
                f"{saudacao}, agradecemos profundamente suas gentis palavras! Saber que nosso trabalho está fazendo a diferença é a maior recompensa que poderíamos ter. Gratidão!"
            ],
            "agradecimento": [
                f"{saudacao}, é nós que agradecemos! Sua confiança e parceria são fundamentais para nós. É um enorme prazer poder contribuir com seu sucesso. Estamos sempre aqui para ajudar! 🙏",
                f"{saudacao}, obrigado por seu agradecimento! Saber que estamos fazendo a diferença para você é o que torna nosso trabalho especial. Conte sempre conosco! 💙",
                f"{saudacao}, gratidão é nossa! Agradecemos por nos permitir fazer parte da sua jornada. Seu sucesso é nossa maior motivação. Estamos à disposição sempre!"
            ],
            "geral": [
                f"{saudacao}, agradecemos sinceramente sua mensagem! Ficamos muito felizes com seu contato e estamos sempre disponíveis para o que precisar. Tenha um excelente dia! 😊",
                f"{saudacao}, que bom receber sua mensagem! Sua opinião é muito importante para nós. Estamos aqui para ajudar no que for necessário. Ótima semana! 🌈",
                f"{saudacao}, obrigado por seu contato! Suas palavras são muito valorizadas por nossa equipe. Estamos sempre à disposição para servir você melhor. 💫"
            ]
        }
    }

    # Determinar o tipo específico de mensagem
    if categoria == "Produtivo":
        if any(p in email_lower for p in ['indisgestão', 'enjoo', 'náusea', 'mal estar', 'febre', 'gripe', 'resfriado', 'temperatura', 'dor']):
            tipo = "saude"
        elif any(p in email_lower for p in ['filho', 'filha', 'criança', 'filhos', 'familia', 'familiar', 'parente', 'esposa', 'marido']):
            tipo = "familia"
        elif any(p in email_lower for p in ['urgente', 'emergência', 'prioridade', 'crítico', 'importante', 'rápido', 'imediat']):
            tipo = "urgente"
        elif any(p in email_lower for p in ['sistema', 'login', 'acesso', 'erro', 'bug', 'problema', 'travou', 'lento']):
            tipo = "tecnico"
        else:
            tipo = "geral"
    else:
        if any(p in email_lower for p in ['natal', 'ano novo', 'réveillon', 'fim de ano']):
            tipo = "natal"
        elif any(p in email_lower for p in ['parabéns', 'congratulações', 'excelente', 'fantástico', 'incrível']):
            tipo = "parabens"
        elif any(p in email_lower for p in ['obrigado', 'agradeço', 'grato', 'gratidão']):
            tipo = "agradecimento"
        else:
            tipo = "geral"

    # Selecionar resposta aleatória do tipo apropriado
    resposta_escolhida = random.choice(respostas[categoria][tipo])
    return resposta_escolhida