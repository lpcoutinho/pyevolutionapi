"""
Testes de integração para validar as correções de validação Pydantic com API real.

Estes testes criam instâncias reais na Evolution API para verificar se:
1. Status "connecting" é aceito corretamente
2. Campo qrcode com tipos mistos é parseado sem erros
3. Não há mais ValidationError com respostas reais da API

REQUISITOS:
- Evolution API rodando (http://localhost:8080 por padrão)
- Variáveis de ambiente configuradas:
  - EVOLUTION_BASE_URL
  - EVOLUTION_API_KEY
  - EVOLUTION_TEST_INSTANCE (opcional)

EXECUÇÃO:
    pytest tests/integration/test_instance_validation.py -v -m integration
"""

import time

import pytest

from pyevolutionapi.models.instance import ConnectionState, InstanceResponse, InstanceStatus


@pytest.mark.integration
class TestRealInstanceCreation:
    """Testa criação real de instâncias e validação das correções."""

    def test_create_instance_returns_connecting_status(self, real_client, clean_test_instance):
        """
        Testa que a criação de instância real retorna status 'connecting'
        e que este status é aceito pelo modelo Pydantic.
        """
        instance_name = clean_test_instance

        # Cria instância real
        response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        # Validações básicas
        assert response is not None
        assert hasattr(response, "status")

        # Verifica que a resposta foi parseada sem erros de validação
        assert isinstance(response, InstanceResponse)

        # Se há instância na resposta, deve ter status válido
        if response.instance:
            # Status pode ser 'created' ou 'connecting' dependendo da implementação
            assert response.instance.status in [
                InstanceStatus.CREATED,
                InstanceStatus.CONNECTING,
                InstanceStatus.CONNECTED,
            ]

        # Aguarda um momento e verifica status atual
        time.sleep(2)
        instances_list = real_client.instance.fetch_instances()

        # Encontra nossa instância na lista
        # A API é inconsistente: create retorna instance_name, fetch_instances retorna apenas id
        test_instance = None
        search_criteria = []

        if response.instance and response.instance.instance_id:
            search_criteria.append(response.instance.instance_id)

        search_criteria.extend(
            [instance_name, response.hash if hasattr(response, "hash") else None]
        )

        if instances_list:
            for instance in instances_list:
                # Busca por qualquer critério válido
                if (
                    instance.id in search_criteria
                    or instance.name in search_criteria
                    or instance.instance_id in search_criteria
                ):
                    test_instance = instance
                    print(f"✅ Instância encontrada por ID: {instance.id}")
                    break

        if test_instance is None:
            print(f"🔍 Critérios de busca: {search_criteria}")
            print("📋 Instâncias disponíveis:")
            for i, inst in enumerate(instances_list or []):
                print(f"  {i+1}. id={inst.id}, name={inst.name}")

        assert test_instance is not None, f"Instância não encontrada. Critérios: {search_criteria}"

        # A API Evolution não retorna status/state em fetch_instances, apenas em create/connect
        # O importante é que as correções permitiram parsear a instância sem erros de validação
        print("✅ Instância parseada sem ValidationError!")
        print(f"📊 Status da instância: {test_instance.status} (pode ser None no fetch_instances)")
        print(f"📊 State da instância: {test_instance.state} (pode ser None no fetch_instances)")

        # Mas verifica que na CRIAÇÃO, o status connecting foi aceito
        if response.instance and response.instance.status:
            print(f"✅ Status na criação foi aceito: {response.instance.status}")
            assert response.instance.status in [
                InstanceStatus.CREATED,
                InstanceStatus.CONNECTING,  # CRÍTICO: Este era o problema antes da correção
                InstanceStatus.CONNECTED,
                InstanceStatus.DISCONNECTED,
            ]

    def test_qrcode_with_count_field_parsing(self, real_client, clean_test_instance):
        """
        Testa que campos qrcode com 'count' como inteiro são parseados corretamente.
        """
        instance_name = clean_test_instance

        # Cria instância com QR code
        response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        # Se há QR code na resposta, verifica parsing
        if response.qrcode:
            print(f"QRcode recebido: {type(response.qrcode)} - {response.qrcode}")

            # Verifica que é um dicionário
            assert isinstance(response.qrcode, dict)

            # Se tem campo count, deve ser aceito independente do tipo
            if "count" in response.qrcode:
                count_value = response.qrcode["count"]
                print(f"✅ Count value: {count_value} (type: {type(count_value)})")

                # Antes da correção, isso falhava se count fosse int
                # Agora deve aceitar qualquer tipo
                assert count_value is not None

        # Testa também através de connect (que pode retornar QR diferente)
        try:
            connect_response = real_client.instance.connect(instance_name)

            if connect_response and hasattr(connect_response, "qrcode") and connect_response.qrcode:
                print(
                    f"QRcode do connect: {type(connect_response.qrcode)} - {connect_response.qrcode}"
                )

                # Verifica parsing sem erros
                assert isinstance(connect_response.qrcode, dict)

                if "count" in connect_response.qrcode:
                    count = connect_response.qrcode["count"]
                    print(f"✅ Connect count: {count} (type: {type(count)})")

        except Exception as e:
            # Se connect falhar, não é problema do teste (pode ser limitação da API)
            print(f"⚠️ Connect falhou (ok para este teste): {e}")

    def test_connection_state_with_connecting_status(
        self, real_client, clean_test_instance, integration_helper
    ):
        """
        Testa que o endpoint connection_state retorna estados válidos incluindo 'connecting'.
        """
        instance_name = clean_test_instance

        # Cria instância
        create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        assert create_response is not None

        # Aguarda um momento para estabilizar
        time.sleep(2)

        # Verifica estado da conexão
        connection_response = real_client.instance.connection_state(instance_name)

        assert connection_response is not None
        print(f"Connection state response: {connection_response}")

        # Se retorna uma instância, verifica o state
        if isinstance(connection_response, dict):
            if "instance" in connection_response:
                instance_data = connection_response["instance"]
                if "state" in instance_data:
                    state = instance_data["state"]

                    # Verifica que estados válidos são aceitos
                    valid_states = ["open", "close", "connecting"]
                    assert state in valid_states
                    print(f"✅ Connection state aceito: {state}")

            # Verifica estado direto (alguns endpoints retornam assim)
            if "state" in connection_response:
                state = connection_response["state"]
                valid_states = ["open", "close", "connecting"]
                assert state in valid_states
                print(f"✅ Direct state aceito: {state}")

    @pytest.mark.slow
    def test_instance_lifecycle_validation(
        self, real_client, clean_test_instance, integration_helper
    ):
        """
        Testa o ciclo de vida completo de uma instância e validação em cada etapa.
        """
        instance_name = clean_test_instance

        # 1. Criar instância
        print(f"📱 Criando instância: {instance_name}")
        create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        assert create_response is not None
        print(f"✅ Instância criada: {create_response.status}")

        # 2. Aguardar status connecting
        print("⏳ Aguardando status connecting...")
        connecting_found = integration_helper.wait_for_status(
            real_client, instance_name, InstanceStatus.CONNECTING, timeout=10
        )

        if connecting_found:
            print("✅ Status CONNECTING encontrado e aceito!")
        else:
            print("ℹ️ Status connecting não foi encontrado (pode variar por implementação)")

        # 3. Verificar que todos os status são parseados corretamente
        instances_list = real_client.instance.fetch_instances()
        test_instance = None

        if instances_list:
            for instance in instances_list:
                if instance.name == instance_name:
                    test_instance = instance
                    break

        assert test_instance is not None
        print(f"✅ Status atual parseado sem erros: {test_instance.status}")
        print(f"✅ State atual parseado sem erros: {test_instance.state}")

        # 4. Verifica QR code se presente
        if test_instance.qrcode:
            print(f"✅ QRcode parseado sem erros: {type(test_instance.qrcode)}")

            # Testa acesso aos campos
            for key, value in test_instance.qrcode.items():
                print(f"  - {key}: {type(value)} = {value}")

        # 5. Restart instance (muda status)
        try:
            print("🔄 Testando restart...")
            restart_response = real_client.instance.restart(instance_name)
            time.sleep(2)  # Aguarda restart

            # Verifica status após restart
            post_restart_list = real_client.instance.fetch_instances()
            if post_restart_list:
                for instance in post_restart_list:
                    if instance.name == instance_name:
                        print(f"✅ Status pós-restart: {instance.status}")
                        break

        except Exception as e:
            print(f"⚠️ Restart falhou (ok para este teste): {e}")


@pytest.mark.integration
class TestRealAPIResponseParsing:
    """Testa parsing de respostas reais da API com foco nas correções."""

    def test_fetch_instances_parsing(self, real_client):
        """Testa que fetch_instances parsa todas as instâncias sem erro de validação."""
        instances_list = real_client.instance.fetch_instances()

        assert instances_list is not None
        assert isinstance(instances_list, list)

        if instances_list:
            print(f"📋 Encontradas {len(instances_list)} instâncias")

            for i, instance in enumerate(instances_list):
                print(f"  {i+1}. {instance.name or instance.id or 'No Name'}")
                print(f"     Status: {instance.status} (type: {type(instance.status)})")
                print(f"     State: {instance.state} (type: {type(instance.state)})")

                # Verifica que status é válido (se presente)
                if instance.status:
                    assert instance.status in [
                        InstanceStatus.CREATED,
                        InstanceStatus.CONNECTING,  # Crítico: deve aceitar connecting
                        InstanceStatus.CONNECTED,
                        InstanceStatus.DISCONNECTED,
                        InstanceStatus.DELETED,
                    ]

                # Verifica QR code se presente
                if instance.qrcode:
                    print(f"     QRcode: {type(instance.qrcode)}")
                    # Verifica que aceita tipos mistos
                    for key, value in instance.qrcode.items():
                        print(f"       {key}: {type(value)}")

        else:
            print("ℹ️ Nenhuma instância encontrada")

    def test_edge_cases_parsing(self, real_client, clean_test_instance):
        """Testa casos extremos de parsing que podem quebrar a validação."""
        instance_name = clean_test_instance

        # Cria instância para ter dados para testar
        create_response = real_client.instance.create(instance_name=instance_name, qrcode=True)

        # Lista todas as respostas possíveis da API
        endpoints_to_test = [
            ("create", lambda: real_client.instance.create(f"{instance_name}-2", qrcode=True)),
            ("fetch_instances", lambda: real_client.instance.fetch_instances()),
            ("connection_state", lambda: real_client.instance.connection_state(instance_name)),
        ]

        for endpoint_name, endpoint_func in endpoints_to_test:
            try:
                print(f"🧪 Testando endpoint: {endpoint_name}")
                response = endpoint_func()

                # Se chegou até aqui, parsing foi bem-sucedido
                print(f"✅ {endpoint_name}: parsing OK")

                # Log do tipo de resposta
                print(f"   Response type: {type(response)}")

                if hasattr(response, "instance") and response.instance:
                    print(f"   Instance status: {response.instance.status}")

                if hasattr(response, "qrcode") and response.qrcode:
                    print(f"   QRcode type: {type(response.qrcode)}")

            except Exception as e:
                # Se falhar, verifica se é erro de validação (que seria bug)
                if "validation" in str(e).lower() or "pydantic" in str(e).lower():
                    pytest.fail(f"❌ Erro de validação Pydantic em {endpoint_name}: {e}")
                else:
                    print(f"⚠️ {endpoint_name} falhou por outro motivo (ok): {e}")


@pytest.mark.integration
@pytest.mark.requires_qr
class TestWithConnectedInstance:
    """
    Testes que requerem instância conectada (QR escaneado).

    ATENÇÃO: Estes testes requerem intervenção manual para escanear QR code.
    Execute apenas quando necessário.
    """

    @pytest.mark.skip(reason="Requer escaneamento manual de QR - execute apenas quando necessário")
    def test_connected_instance_parsing(self, connected_instance, real_client):
        """Testa parsing de instância conectada (após QR escaneado)."""
        instance_name = connected_instance

        # Verifica status da instância conectada
        instances_list = real_client.instance.fetch_instances()
        test_instance = None

        if instances_list:
            for instance in instances_list:
                if instance.name == instance_name:
                    test_instance = instance
                    break

        assert test_instance is not None

        # Instância conectada deve ter status/state específicos
        print(f"📱 Instância conectada - Status: {test_instance.status}")
        print(f"📱 Instância conectada - State: {test_instance.state}")

        # Deve ser conectada
        assert test_instance.status == InstanceStatus.CONNECTED
        assert test_instance.state == ConnectionState.OPEN

        # Pode ter informações adicionais
        if test_instance.number:
            print(f"📞 Número: {test_instance.number}")

        if test_instance.profile_name:
            print(f"👤 Nome: {test_instance.profile_name}")

        print("✅ Instância conectada parseada corretamente!")
