#!/usr/bin/env python3
"""
Script para executar testes de integração com a Evolution API real.

Este script:
1. Carrega configurações do arquivo .env.integration
2. Verifica se a Evolution API está acessível
3. Executa os testes de integração
4. Fornece relatório dos resultados

USO:
    python run_integration_tests.py [--setup] [--all] [--quick]

OPÇÕES:
    --setup     : Mostra instruções de configuração e sai
    --all       : Executa todos os testes (incluindo os que requerem QR)
    --quick     : Executa apenas testes rápidos (pula testes marcados como 'slow')
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def load_integration_env():
    """Carrega variáveis de ambiente para testes de integração."""
    integration_env = Path(".env.integration")

    if not integration_env.exists():
        print("❌ Arquivo .env.integration não encontrado!")
        print("\n📋 Configure os testes de integração:")
        print("1. Copie .env.integration.example para .env.integration")
        print("2. Configure suas credenciais reais da Evolution API")
        print("3. Execute novamente este script")
        return False

    load_dotenv(integration_env)
    return True


def check_evolution_api():
    """Verifica se a Evolution API está acessível."""
    base_url = os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY")

    if not api_key:
        print("❌ EVOLUTION_API_KEY não configurado no .env.integration")
        return False

    try:
        # Tenta fazer um health check básico
        health_url = f"{base_url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=10)

        if response.status_code == 200:
            print(f"✅ Evolution API acessível: {base_url}")
            return True
        else:
            print(f"⚠️ Evolution API respondeu com status {response.status_code}")
            print("Continuando mesmo assim...")
            return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Não foi possível conectar na Evolution API: {e}")
        print(f"URL testada: {base_url}")
        print("\n🔧 Verifique:")
        print("- Evolution API está rodando?")
        print("- URL está correta no .env.integration?")
        print("- Firewall/proxy não está bloqueando?")
        return False


def show_setup_instructions():
    """Mostra instruções detalhadas de configuração."""
    print(
        """
🚀 CONFIGURAÇÃO DOS TESTES DE INTEGRAÇÃO
========================================

1️⃣ CONFIGURE A EVOLUTION API:
   - Certifique-se que está rodando (normalmente em http://localhost:8080)
   - Acesse o manager web para obter sua API key
   - Anote a URL base e a API key

2️⃣ CONFIGURE O ARQUIVO DE AMBIENTE:
   cp .env.integration.example .env.integration

   Edite .env.integration e configure:
   - EVOLUTION_BASE_URL=http://localhost:8080
   - EVOLUTION_API_KEY=sua-chave-aqui

3️⃣ EXECUTE OS TESTES:
   python run_integration_tests.py

📋 TIPOS DE TESTE DISPONÍVEIS:
   --quick     : Testes rápidos (recomendado para desenvolvimento)
   --all       : Todos os testes (inclui testes que requerem QR)
   (padrão)    : Testes de integração normais

🔍 COMANDOS PYTEST DIRETOS:
   pytest tests/integration/ -v -m integration
   pytest tests/integration/ -v -m "integration and not slow"
   pytest tests/integration/ -v -m requires_qr

⚠️ IMPORTANTE:
   - Estes testes criam instâncias REAIS na Evolution API
   - Use apenas para desenvolvimento/teste
   - Instâncias de teste são limpas automaticamente
   - NÃO execute em produção
"""
    )


def run_tests(test_type="normal"):
    """Executa os testes de integração."""
    base_cmd = ["python", "-m", "pytest", "tests/integration/", "-v"]

    if test_type == "quick":
        # Executa testes rápidos apenas
        base_cmd.extend(["-m", "integration and not slow"])
        print("🏃 Executando testes rápidos de integração...")

    elif test_type == "all":
        # Executa todos os testes
        base_cmd.extend(["-m", "integration"])
        print("🔄 Executando TODOS os testes de integração (incluindo QR)...")
        print("⚠️  Alguns testes podem requerer escaneamento manual de QR code!")

    else:
        # Executa testes normais (sem QR, com alguns slow)
        base_cmd.extend(["-m", "integration and not requires_qr"])
        print("🧪 Executando testes de integração padrão...")

    print(f"Comando: {' '.join(base_cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(base_cmd, check=False)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⚡ Testes interrompidos pelo usuário")
        return False
    except Exception as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Executa testes de integração com Evolution API real"
    )
    parser.add_argument(
        "--setup", action="store_true", help="Mostra instruções de configuração e sai"
    )
    parser.add_argument(
        "--all", action="store_true", help="Executa todos os testes (incluindo os que requerem QR)"
    )
    parser.add_argument("--quick", action="store_true", help="Executa apenas testes rápidos")

    args = parser.parse_args()

    if args.setup:
        show_setup_instructions()
        return 0

    print("🧪 TESTES DE INTEGRAÇÃO - PYEVOLUTION API")
    print("=" * 50)

    # 1. Carrega configuração
    print("📁 Carregando configuração...")
    if not load_integration_env():
        return 1

    # 2. Verifica API
    print("🔍 Verificando Evolution API...")
    if not check_evolution_api():
        print("\n💡 Use --setup para ver instruções de configuração")
        return 1

    # 3. Executa testes
    test_type = "all" if args.all else "quick" if args.quick else "normal"
    success = run_tests(test_type)

    if success:
        print("\n🎉 Testes de integração concluídos com sucesso!")
        print("✅ As correções de validação Pydantic estão funcionando!")
    else:
        print("\n💥 Alguns testes falharam")
        print("🔍 Verifique os logs acima para detalhes")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
