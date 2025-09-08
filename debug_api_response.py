#!/usr/bin/env python3
"""
Script de debug para ver exatamente o que a Evolution API está retornando.
"""

import os

from dotenv import load_dotenv

from pyevolutionapi import EvolutionClient

# Carrega configuração
load_dotenv(".env.integration")


def main():
    client = EvolutionClient(
        base_url=os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080"),
        api_key=os.getenv("EVOLUTION_API_KEY"),
        debug=True,
    )

    print("🔍 Debug da Evolution API\n")

    # 1. Criar instância de teste
    test_name = "debug-test-instance"
    print(f"📱 Criando instância: {test_name}")

    try:
        # Delete se existir
        try:
            client.instance.delete(test_name)
            print("🗑️ Instância anterior deletada")
        except Exception:
            pass

        # Cria nova
        create_response = client.instance.create(instance_name=test_name, qrcode=True)

        print("✅ Instância criada com sucesso!")
        print(f"Response type: {type(create_response)}")
        print(f"Response: {create_response}")

        if hasattr(create_response, "instance") and create_response.instance:
            print("\nInstância retornada na criação:")
            instance = create_response.instance
            print(f"  - instance_name: {instance.instance_name}")
            print(f"  - instance_id: {instance.instance_id}")
            print(f"  - id: {instance.id}")
            print(f"  - status: {instance.status}")
            print(f"  - property .name: {instance.name}")

        # 2. Buscar todas as instâncias
        print("\n📋 Buscando todas as instâncias...")
        instances_list = client.instance.fetch_instances()

        print(f"Total encontradas: {len(instances_list)}")

        for i, instance in enumerate(instances_list):
            print(f"\n--- Instância {i+1} ---")
            print(f"Type: {type(instance)}")
            print(f"instance_name: {repr(instance.instance_name)}")
            print(f"instance_id: {repr(instance.instance_id)}")
            print(f"id: {repr(instance.id)}")
            print(f"status: {repr(instance.status)}")
            print(f"state: {repr(instance.state)}")
            print(f"property .name: {repr(instance.name)}")
            print(f"profile_name: {repr(instance.profile_name)}")

            # Mostra campos da API real
            if instance.Setting:
                print(f"Setting: {instance.Setting}")

            # Verifica se é nossa instância de teste
            is_test = (
                instance.instance_name == test_name
                or instance.instance_id == test_name
                or instance.id == test_name
                or instance.name == test_name
            )

            if is_test:
                print("🎯 ESTA É NOSSA INSTÂNCIA DE TESTE!")

        # 3. Cleanup
        print("\n🗑️ Limpando instância de teste...")
        client.instance.delete(test_name)
        print("✅ Cleanup concluído")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
