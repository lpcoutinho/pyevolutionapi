#!/usr/bin/env python3
"""
Script para limpeza manual de instâncias na Evolution API.

Este script permite:
1. Listar todas as instâncias existentes
2. Remover instâncias específicas
3. Remover instâncias de teste (nomes que começam com 'test', 'pytest', etc)
4. Limpeza completa (cuidado!)

Use com cuidado - remove instâncias REAIS da Evolution API!

Exemplos:
    python cleanup_instances.py --list                    # Lista instâncias
    python cleanup_instances.py --remove test-instance    # Remove específica
    python cleanup_instances.py --clean-test             # Remove de teste
    python cleanup_instances.py --confirm-clean-all      # Remove TODAS (CUIDADO!)
"""

import argparse
import os
import sys
import time
from typing import List

from dotenv import load_dotenv

from pyevolutionapi import EvolutionClient


def list_instances(client: EvolutionClient) -> List[dict]:
    """Lista todas as instâncias na Evolution API."""
    try:
        instances = client.instance.fetch_instances()

        instance_data = []
        for i, instance in enumerate(instances):
            data = {
                "index": i + 1,
                "id": instance.id,
                "name": instance.name or "No Name",
                "status": instance.status,
                "state": instance.state,
                "profile_name": instance.profile_name or "No Profile",
                "integration": instance.integration,
                "created_at": instance.created_at,
            }
            instance_data.append(data)

        return instance_data

    except Exception as e:
        print(f"❌ Erro ao listar instâncias: {e}")
        return []


def is_test_instance(instance_id: str, name: str) -> bool:
    """Verifica se é uma instância de teste baseada no nome/ID."""
    test_patterns = [
        "test",
        "pytest",
        "debug",
        "temp",
        "demo",
        "example",
        "sample",
        "trial",
        "qrcode-test",
        "connect-test",
        "edge-test",
    ]

    check_strings = [instance_id or "", name or ""]

    for check_str in check_strings:
        if check_str:
            check_lower = check_str.lower()
            for pattern in test_patterns:
                if pattern in check_lower:
                    return True

    return False


def remove_instance(client: EvolutionClient, identifier: str) -> bool:
    """
    Remove uma instância específica.

    Args:
        client: Cliente da Evolution API
        identifier: ID ou nome da instância

    Returns:
        bool: True se removida com sucesso
    """
    try:
        client.instance.delete(identifier)
        print(f"✅ Removida: {identifier}")
        return True

    except Exception as e:
        print(f"❌ Erro ao remover {identifier}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Limpeza de instâncias da Evolution API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s --list                          Lista todas as instâncias
  %(prog)s --remove test-instance          Remove instância específica
  %(prog)s --clean-test                   Remove instâncias de teste
  %(prog)s --confirm-clean-all            Remove TODAS as instâncias (CUIDADO!)

⚠️  ATENÇÃO: Este script remove instâncias REAIS da Evolution API!
        """,
    )

    parser.add_argument("--list", action="store_true", help="Lista todas as instâncias")
    parser.add_argument(
        "--remove",
        type=str,
        metavar="ID_OR_NAME",
        help="Remove instância específica por ID ou nome",
    )
    parser.add_argument(
        "--clean-test",
        action="store_true",
        help="Remove instâncias de teste (nomes com test, pytest, etc)",
    )
    parser.add_argument(
        "--confirm-clean-all", action="store_true", help="Remove TODAS as instâncias (PERIGOSO!)"
    )

    args = parser.parse_args()

    if not any([args.list, args.remove, args.clean_test, args.confirm_clean_all]):
        parser.print_help()
        return 1

    # Carrega configuração
    load_dotenv(".env.integration")

    api_key = os.getenv("EVOLUTION_API_KEY")
    if not api_key:
        print("❌ EVOLUTION_API_KEY não configurado no .env.integration")
        return 1

    client = EvolutionClient(
        base_url=os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080"),
        api_key=api_key,
        timeout=30.0,
    )

    print("🧹 LIMPEZA DE INSTÂNCIAS - EVOLUTION API")
    print("=" * 50)

    # Lista instâncias
    print("📋 Carregando instâncias...")
    instances = list_instances(client)

    if not instances:
        print("ℹ️ Nenhuma instância encontrada")
        return 0

    # Ação: Listar
    if args.list:
        print(f"\n📋 INSTÂNCIAS ENCONTRADAS ({len(instances)}):")
        print("-" * 80)

        for instance in instances:
            test_flag = " [TESTE]" if is_test_instance(instance["id"], instance["name"]) else ""
            print(f"{instance['index']:2}. {instance['id']}")
            print(f"    Nome: {instance['name']}{test_flag}")
            print(f"    Profile: {instance['profile_name']}")
            print(f"    Status: {instance['status']} | State: {instance['state']}")
            print(f"    Integration: {instance['integration']}")
            if instance["created_at"]:
                print(f"    Criado: {instance['created_at']}")
            print()

    # Ação: Remover específica
    elif args.remove:
        instance_id = args.remove
        print(f"🗑️ Removendo instância: {instance_id}")

        # Verifica se existe
        found = False
        for instance in instances:
            if instance["id"] == instance_id or instance["name"] == instance_id:
                found = True
                break

        if not found:
            print(f"⚠️ Instância '{instance_id}' não encontrada")
            print("💡 Use --list para ver instâncias disponíveis")
            return 1

        if remove_instance(client, instance_id):
            print("✅ Instância removida com sucesso!")
        else:
            print("❌ Falha na remoção")
            return 1

    # Ação: Limpar instâncias de teste
    elif args.clean_test:
        test_instances = [
            instance for instance in instances if is_test_instance(instance["id"], instance["name"])
        ]

        if not test_instances:
            print("ℹ️ Nenhuma instância de teste encontrada")
            return 0

        print(f"🧪 INSTÂNCIAS DE TESTE ENCONTRADAS ({len(test_instances)}):")
        for instance in test_instances:
            print(f"  - {instance['id']} ({instance['name']})")

        confirm = input(f"\n⚠️ Remover {len(test_instances)} instância(s) de teste? [y/N]: ")

        if confirm.lower() in ["y", "yes", "s", "sim"]:
            removed = 0
            for instance in test_instances:
                if remove_instance(client, instance["id"]):
                    removed += 1
                time.sleep(0.5)  # Evita rate limiting

            print(f"\n✅ {removed}/{len(test_instances)} instâncias de teste removidas")
        else:
            print("❌ Operação cancelada")

    # Ação: Limpar TODAS (perigoso!)
    elif args.confirm_clean_all:
        print(f"⚠️ ATENÇÃO: REMOVER TODAS AS {len(instances)} INSTÂNCIAS!")
        print("🚨 Esta operação é IRREVERSÍVEL!")
        print("🚨 Todas as instâncias da Evolution API serão PERDIDAS!")

        for instance in instances[:5]:  # Mostra algumas
            print(f"  - {instance['id']} ({instance['name']})")

        if len(instances) > 5:
            print(f"  ... e mais {len(instances) - 5} instâncias")

        print("\n" + "=" * 50)
        confirm1 = input("Digite 'CONFIRMO' para continuar: ")

        if confirm1 != "CONFIRMO":
            print("❌ Operação cancelada")
            return 0

        confirm2 = input("Tem CERTEZA ABSOLUTA? Digite 'SIM REMOVER TODAS': ")

        if confirm2 != "SIM REMOVER TODAS":
            print("❌ Operação cancelada")
            return 0

        print(f"\n🗑️ Removendo {len(instances)} instâncias...")
        removed = 0

        for instance in instances:
            if remove_instance(client, instance["id"]):
                removed += 1
            time.sleep(0.5)  # Evita rate limiting

        print(f"\n💥 {removed}/{len(instances)} instâncias removidas")

        if removed == len(instances):
            print("✅ Limpeza completa realizada!")
        else:
            print("⚠️ Algumas instâncias podem não ter sido removidas")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚡ Operação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")
        sys.exit(1)
