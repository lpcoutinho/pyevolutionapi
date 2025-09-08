"""
Configuração e fixtures para testes de integração com a Evolution API real.

Estes testes requerem uma instância da Evolution API rodando e configurada.
Configure as variáveis de ambiente necessárias:
- EVOLUTION_BASE_URL
- EVOLUTION_API_KEY
- EVOLUTION_TEST_INSTANCE (nome da instância para testes)
"""

import os
import time
from typing import Generator

import pytest

from pyevolutionapi import EvolutionClient
from pyevolutionapi.models.instance import ConnectionState, InstanceStatus


@pytest.fixture(scope="session")
def api_config():
    """Configuração da API real para testes de integração."""
    base_url = os.getenv("EVOLUTION_BASE_URL", "http://localhost:8080")
    api_key = os.getenv("EVOLUTION_API_KEY")

    if not api_key:
        pytest.skip("EVOLUTION_API_KEY não configurado - pulando testes de integração")

    return {
        "base_url": base_url,
        "api_key": api_key,
        "timeout": 60.0,  # Timeout maior para testes reais
    }


@pytest.fixture(scope="session")
def real_client(api_config):
    """Cliente configurado para usar API real."""
    client = EvolutionClient(
        base_url=api_config["base_url"],
        api_key=api_config["api_key"],
        timeout=api_config["timeout"],
        debug=True,  # Habilita logs para debug
    )

    # Testa se API está acessível
    try:
        health = client.health_check()

        # health_check pode retornar boolean ou dict
        if isinstance(health, dict):
            if not health.get("status") == "ok":
                pytest.skip("Evolution API não está acessível")
        elif isinstance(health, bool):
            if not health:
                pytest.skip("Evolution API não está acessível")
        else:
            # Se retornou algo inesperado, considera como inacessível
            pytest.skip("Evolution API retornou resposta inesperada")

    except Exception as e:
        pytest.skip(f"Evolution API não está acessível: {e}")

    yield client


@pytest.fixture
def test_instance_name():
    """Nome da instância para testes."""
    return os.getenv("EVOLUTION_TEST_INSTANCE", f"pytest-{int(time.time())}")


@pytest.fixture
def clean_test_instance(real_client, test_instance_name) -> Generator[str, None, None]:
    """
    Fixture que cria uma instância limpa para testes e faz cleanup após o teste.

    Yields:
        str: Nome da instância criada
    """
    instance_name = test_instance_name

    # Cleanup antes do teste (caso tenha ficado de testes anteriores)
    try:
        real_client.instance.delete(instance_name)
        time.sleep(2)  # Aguarda cleanup
    except Exception:
        pass  # Ignora erros de cleanup inicial

    yield instance_name

    # Cleanup após o teste
    try:
        real_client.instance.delete(instance_name)
    except Exception:
        pass  # Ignora erros de cleanup final


@pytest.fixture
def connected_instance(real_client, clean_test_instance) -> Generator[str, None, None]:
    """
    Fixture que cria uma instância já conectada (com QR escaneado).

    NOTA: Este fixture requer intervenção manual para escanear o QR code.
    Use apenas em testes que realmente precisam de instância conectada.
    """
    instance_name = clean_test_instance

    # Cria instância
    response = real_client.instance.create(instance_name=instance_name, qrcode=True)

    if response.qr_code_base64:
        print(f"\n🔲 ESCANEIE O QR CODE para conectar a instância '{instance_name}':")
        print(f"QR Code (base64): {response.qr_code_base64[:100]}...")
        print("Aguardando conexão... (timeout em 60s)")

        # Aguarda conexão por até 60 segundos
        for attempt in range(12):  # 12 x 5s = 60s
            time.sleep(5)
            status = real_client.instance.connection_state(instance_name)
            if status.get("state") == "open":
                print("✅ Instância conectada!")
                break
            print(f"⏳ Aguardando conexão... tentativa {attempt + 1}/12")
        else:
            pytest.skip("Timeout: QR code não foi escaneado em 60s")

    yield instance_name


class IntegrationTestHelper:
    """Helper class com métodos úteis para testes de integração."""

    @staticmethod
    def wait_for_status(
        client: EvolutionClient,
        instance_name: str,
        expected_status: InstanceStatus,
        timeout: int = 30,
    ) -> bool:
        """
        Aguarda até que a instância atinja o status esperado.

        Args:
            client: Cliente da Evolution API
            instance_name: Nome da instância
            expected_status: Status esperado
            timeout: Timeout em segundos

        Returns:
            bool: True se status foi atingido, False se timeout
        """
        for _ in range(timeout):
            try:
                instances = client.instance.fetch_instances()
                for instance in instances.instances or []:
                    if instance.instance_name == instance_name:
                        if instance.status == expected_status:
                            return True
                        break
            except Exception:
                pass
            time.sleep(1)
        return False

    @staticmethod
    def wait_for_connection(
        client: EvolutionClient,
        instance_name: str,
        expected_state: ConnectionState,
        timeout: int = 30,
    ) -> bool:
        """
        Aguarda até que a instância atinja o estado de conexão esperado.

        Args:
            client: Cliente da Evolution API
            instance_name: Nome da instância
            expected_state: Estado de conexão esperado
            timeout: Timeout em segundos

        Returns:
            bool: True se estado foi atingido, False se timeout
        """
        for _ in range(timeout):
            try:
                status = client.instance.connection_state(instance_name)
                if status.get("state") == expected_state.value:
                    return True
            except Exception:
                pass
            time.sleep(1)
        return False


@pytest.fixture
def integration_helper():
    """Fixture que fornece helper methods para testes de integração."""
    return IntegrationTestHelper


# Markers para diferentes tipos de testes de integração
pytest_plugins = []


def pytest_configure(config):
    """Configura markers personalizados."""
    config.addinivalue_line(
        "markers", "integration: marca testes que usam API real (podem ser lentos)"
    )
    config.addinivalue_line(
        "markers", "requires_qr: marca testes que requerem escaneamento manual de QR"
    )
    config.addinivalue_line("markers", "slow: marca testes que são lentos (>10s)")
