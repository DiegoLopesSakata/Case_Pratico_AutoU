from classifier import classify_email, gerar_resposta, OPENAI_API_KEY
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def verificar_configuracao():
    """Verificar configuração das APIs"""
    print("🔍 Verificando configuração...")
    
    # Verificar OpenAI
    if OPENAI_API_KEY and OPENAI_API_KEY != 'sua_chave_openai_aqui':
        print("✅ OpenAI configurada - IA real disponível")
        return "openai"
    else:
        print("⚠️  OpenAI não configurada")
        return "fallback"

def test_casos_reais():
    """Testar com casos reais"""
    print("\n🧪 Testando casos reais...")
    
    testes = [
        ("Olá, estou com um problema no sistema de login", "Produtivo"),
        ("Parabéns pelo excelente trabalho da equipe!", "Improdutivo"),
        ("Preciso me ausentar hoje por motivo de saúde", "Produtivo"),
        ("Obrigado por todo o suporte durante o projeto", "Improdutivo"),
        ("Estou com indisgestão e não vou conseguir trabalhar hoje", "Produtivo"),
        ("Feliz Natal para toda a equipe!", "Improdutivo"),
        ("URGENTE: servidor está offline", "Produtivo"),
        ("Agradeço a compreensão de todos", "Improdutivo")
    ]
    
    acertos = 0
    total = len(testes)
    
    for i, (email, esperado) in enumerate(testes, 1):
        print(f"\n{'='*60}")
        print(f"📝 Teste {i}: {email}")
        categoria = classify_email(email)
        status = "✅" if categoria == esperado else "❌"
        if categoria == esperado:
            acertos += 1
        print(f"{status} Categoria: {categoria} (esperado: {esperado})")
        
        resposta = gerar_resposta(categoria, email)
        print(f"💡 Resposta: {resposta}")
    
    print(f"\n🎯 Resultado Final: {acertos}/{total} acertos ({acertos/total*100:.1f}%)")

def test_email_indisgestao():
    """Teste específico para o caso de indisgestão"""
    print(f"\n{'='*60}")
    print("🧪 Teste Especial: Caso de Indisgestão")
    print("="*60)
    
    email_indisgestao = "Assunto: Indisgestão\n\nOlá gestores.\n\nTerei que me ausentar hoje, pois estou com indisgestão.\n\nAgradeço a compreensão."
    categoria = classify_email(email_indisgestao)
    resposta = gerar_resposta(categoria, email_indisgestao)
    
    print(f"📧 Email: {email_indisgestao}")
    print(f"🎯 Categoria: {categoria}")
    print(f"💡 Resposta: {resposta}")
    
    # Verificar se classificou corretamente como Produtivo
    if categoria == "Produtivo":
        print("✅ SUCESSO: Email de indisgestão classificado corretamente como Produtivo!")
    else:
        print("❌ PROBLEMA: Email de indisgestão deveria ser Produtivo!")

def test_desempenho():
    """Teste de desempenho do sistema"""
    print(f"\n{'='*60}")
    print("⏱️  Teste de Desempenho")
    print("="*60)
    
    import time
    
    # Teste com email produtivo
    email = "Olá, estou com um problema urgente no sistema de relatórios. Não consigo gerar os documentos importantes para a reunião de hoje."
    
    start_time = time.time()
    categoria = classify_email(email)
    tempo_classificacao = time.time() - start_time
    
    start_time = time.time()
    resposta = gerar_resposta(categoria, email)
    tempo_resposta = time.time() - start_time
    
    print(f"⏰ Tempo classificação: {tempo_classificacao:.3f}s")
    print(f"⏰ Tempo resposta: {tempo_resposta:.3f}s")
    print(f"📧 Categoria: {categoria}")
    print(f"💡 Resposta: {resposta}")

if __name__ == "__main__":
    # Verificar configuração
    config = verificar_configuracao()
    
    if config == "openai":
        print("\n🚀 Modo: IA Real (OpenAI)")
    else:
        print("\n🚀 Modo: Fallback Inteligente")
    
    # Executar testes
    test_casos_reais()
    test_email_indisgestao()
    test_desempenho()
    
    print(f"\n{'='*60}")
    print("🚀 SISTEMA PRONTO PARA USO!")
    print("="*60)
    print("Execute: python app.py")
    print("Acesse: http://localhost:5000")