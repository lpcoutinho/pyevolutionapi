# PyEvolutionAPI - Claude Assistant Documentation

**PyEvolutionAPI** é uma biblioteca Python moderna e type-safe para integração com a Evolution API, facilitando o desenvolvimento de soluções WhatsApp.

## 📋 Visão Geral do Projeto

### Informações Básicas
- **Nome**: pyevolutionapi
- **Versão**: 0.1.0
- **Autor**: Luiz Paulo Coutinho
- **Licença**: MIT
- **Linguagem**: Python 3.8+
- **Repositório**: https://github.com/lpcoutinho/pyevolution

### Propósito
Esta biblioteca fornece uma interface Python limpa e intuitiva para a Evolution API v2.2.2, permitindo:
- Gerenciamento de instâncias WhatsApp
- Envio de mensagens (texto, mídia, áudio, etc.)
- Operações de chat e contatos
- Gerenciamento de grupos
- Configuração de webhooks e integrações

## 🏗️ Arquitetura do Projeto

### Estrutura de Diretórios
```
pyevolutionapi/
├── pyevolutionapi/           # Pacote principal
│   ├── __init__.py       # Exports e factory functions
│   ├── client.py         # Cliente principal
│   ├── auth.py           # Sistema de autenticação
│   ├── exceptions.py     # Exceções customizadas
│   ├── models/           # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── base.py       # Modelos base
│   │   ├── instance.py   # Modelos de instância
│   │   ├── message.py    # Modelos de mensagem
│   │   ├── group.py      # Modelos de grupo
│   │   ├── chat.py       # Modelos de chat
│   │   └── webhook.py    # Modelos de webhook
│   ├── resources/        # Recursos da API
│   │   ├── __init__.py
│   │   ├── base.py       # Classe base para recursos
│   │   ├── instance.py   # Gerenciamento de instâncias
│   │   ├── message.py    # Envio de mensagens
│   │   ├── chat.py       # Operações de chat
│   │   ├── group.py      # Gerenciamento de grupos
│   │   ├── profile.py    # Configurações de perfil
│   │   └── webhook.py    # Configuração de webhooks
│   └── utils/            # Utilitários
├── tests/                # Testes
│   ├── conftest.py       # Configuração do pytest
│   ├── unit/             # Testes unitários
│   └── integration/      # Testes de integração
├── examples/             # Exemplos de uso
├── docs/                 # Documentação
└── .env.example          # Exemplo de configuração
```

### Componentes Principais

#### 1. Cliente Principal (`EvolutionClient`)
- **Localização**: `pyevolutionapi/client.py`
- **Responsabilidade**: Gerenciar conexões HTTP, autenticação e coordenar recursos
- **Recursos**:
  - Suporte síncrono e assíncrono
  - Retry automático com backoff exponencial
  - Rate limiting inteligente
  - Context manager support
  - Health checks

#### 2. Sistema de Autenticação (`AuthHandler`)
- **Localização**: `pyevolutionapi/auth.py`
- **Responsabilidade**: Gerenciar autenticação global e por instância
- **Recursos**:
  - API key global
  - Tokens por instância
  - Headers automáticos
  - Suporte a Bearer token e API key

#### 3. Modelos de Dados (Pydantic)
- **Localização**: `pyevolutionapi/models/`
- **Responsabilidade**: Validação de dados, serialização/deserialização
- **Recursos**:
  - Type hints completos
  - Validação automática
  - Conversão para/de JSON
  - Alias support para compatibilidade com API

#### 4. Recursos da API
- **Localização**: `pyevolutionapi/resources/`
- **Responsabilidade**: Implementar operações específicas da API
- **Recursos**:
  - Métodos síncronos e assíncronos
  - Validação de parâmetros
  - Tratamento de erros específicos
  - Response parsing automático

## 🔧 Configuração e Uso

### Instalação
```bash
pip install pyevolutionapi
```

### Configuração Básica
```python
from pyevolutionapi import EvolutionClient

# Via parâmetros
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-api-key",
    default_instance="my-instance"
)

# Via variáveis de ambiente
client = EvolutionClient()  # Usa .env automaticamente
```

### Variáveis de Ambiente
```bash
# Obrigatórias
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your-global-api-key

# Opcionais
EVOLUTION_INSTANCE_NAME=default-instance
EVOLUTION_DEBUG=false
EVOLUTION_REQUEST_TIMEOUT=30
EVOLUTION_MAX_RETRIES=3
```

### Exemplo de Uso Básico
```python
from pyevolutionapi import EvolutionClient

# Criar cliente
client = EvolutionClient(
    base_url="http://localhost:8080",
    api_key="your-key"
)

# Criar instância
instance = client.instance.create(
    instance_name="meu-bot",
    qrcode=True
)

# Enviar mensagem
response = client.messages.send_text(
    instance="meu-bot",
    number="5511999999999",
    text="Olá do PyEvolution!"
)

# Verificar resposta
if response.is_success:
    print(f"Mensagem enviada: {response.message_id}")
```

## 📚 Recursos Disponíveis

### 1. Instâncias (`client.instance`)
- `create()` - Criar nova instância
- `fetch_instances()` - Listar instâncias
- `connect()` - Conectar instância (obter QR code)
- `restart()` - Reiniciar instância
- `connection_state()` - Verificar status de conexão
- `set_presence()` - Definir presença
- `logout()` - Desconectar instância
- `delete()` - Deletar instância

### 2. Mensagens (`client.messages`)
- `send_text()` - Enviar texto
- `send_media()` - Enviar mídia (imagem, vídeo, documento)
- `send_audio()` - Enviar áudio
- `send_location()` - Enviar localização
- `send_contact()` - Enviar contato
- `send_reaction()` - Enviar reação
- `send_sticker()` - Enviar sticker
- `send_poll()` - Enviar enquete
- `send_status()` - Enviar status/story

### 3. Chat (`client.chat`)
- `whatsapp_numbers()` - Verificar números no WhatsApp
- `mark_as_read()` - Marcar mensagens como lidas
- `fetch_profile_picture()` - Obter foto de perfil
- `find_contacts()` - Buscar contatos
- `find_messages()` - Buscar mensagens
- `find_chats()` - Buscar conversas
- `send_presence()` - Enviar presença (digitando, etc.)
- `update_block_status()` - Bloquear/desbloquear contato

### 4. Grupos (`client.group`)
- `create()` - Criar grupo
- `update_picture()` - Atualizar foto do grupo
- `update_subject()` - Atualizar nome do grupo
- `update_description()` - Atualizar descrição
- `get_invite_code()` - Obter código de convite
- `revoke_invite_code()` - Revogar código de convite
- `update_participant()` - Gerenciar participantes
- `fetch_all_groups()` - Listar todos os grupos
- `get_participants()` - Obter participantes
- `leave_group()` - Sair do grupo

### 5. Perfil (`client.profile`)
- `fetch_profile()` - Obter perfil
- `fetch_business_profile()` - Obter perfil comercial
- `update_name()` - Atualizar nome
- `update_status()` - Atualizar status
- `update_picture()` - Atualizar foto
- `remove_picture()` - Remover foto
- `fetch_privacy_settings()` - Obter configurações de privacidade
- `update_privacy_settings()` - Atualizar privacidade

### 6. Webhooks (`client.webhook`)
- `set_webhook()` - Configurar webhook
- `find_webhook()` - Obter configuração de webhook
- `set_websocket()` - Configurar WebSocket
- `set_rabbitmq()` - Configurar RabbitMQ
- `set_sqs()` - Configurar AWS SQS

## 🔄 Suporte Assíncrono

Todos os métodos possuem versões assíncronas:

```python
import asyncio
from pyevolutionapi import EvolutionClient

async def exemplo_async():
    client = EvolutionClient()
    
    async with client:  # Context manager assíncrono
        # Criar instância
        instance = await client.instance.acreate(
            instance_name="async-bot"
        )
        
        # Enviar mensagens em paralelo
        tasks = [
            client.messages.asend_text(
                instance="async-bot",
                number=f"5511{9999999+i:08d}",
                text=f"Mensagem {i}"
            )
            for i in range(5)
        ]
        
        results = await asyncio.gather(*tasks)
        print(f"Enviadas {len(results)} mensagens")

# Executar
asyncio.run(exemplo_async())
```

## 🛠️ Tratamento de Erros

### Hierarquia de Exceções
```python
EvolutionAPIError                    # Base para todas as exceções
├── AuthenticationError             # Erro de autenticação (401)
├── NotFoundError                   # Recurso não encontrado (404)
├── ValidationError                 # Erro de validação (400)
├── ConnectionError                 # Erro de conexão
├── TimeoutError                    # Timeout de request
├── RateLimitError                  # Rate limit excedido (429)
├── WebhookError                    # Erro de webhook
├── InstanceError                   # Erro de instância
├── MessageError                    # Erro de mensagem
│   └── MediaError                  # Erro de mídia
└── GroupError                      # Erro de grupo
```

### Exemplo de Tratamento
```python
from pyevolutionapi import EvolutionClient
from pyevolution.exceptions import (
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError
)

try:
    client = EvolutionClient()
    response = client.messages.send_text(
        instance="test",
        number="invalid",
        text="teste"
    )
except AuthenticationError as e:
    print(f"Erro de autenticação: {e}")
except ValidationError as e:
    print(f"Dados inválidos: {e}")
    print(f"Erros específicos: {e.errors}")
except RateLimitError as e:
    print(f"Rate limit excedido, tentar novamente em {e.retry_after}s")
except NotFoundError as e:
    print(f"Instância não encontrada: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

## 🧪 Testes

### Estrutura de Testes
- **Unit Tests**: `tests/unit/` - Testes isolados de cada componente
- **Integration Tests**: `tests/integration/` - Testes com API real
- **Fixtures**: `tests/conftest.py` - Configurações compartilhadas

### Executar Testes
```bash
# Todos os testes
pytest

# Apenas unit tests
pytest tests/unit/

# Com cobertura
pytest --cov=pyevolution --cov-report=html

# Testes específicos
pytest tests/unit/test_client.py::TestEvolutionClient::test_health_check
```

### Mocks e Fixtures
```python
# Fixture de cliente para testes
@pytest.fixture
def client():
    return EvolutionClient(
        base_url="http://localhost:8080",
        api_key="test-key",
        default_instance="test-instance"
    )

# Mock de resposta da API
@pytest.fixture
def mock_response():
    response = Mock(spec=httpx.Response)
    response.status_code = 200
    response.is_success = True
    response.json.return_value = {"status": "success"}
    return response
```

## 📦 Distribuição e Publicação

### Build do Pacote
```bash
# Instalar dependências de build
pip install build twine

# Fazer build
python -m build

# Verificar pacote
twine check dist/*

# Upload para PyPI Test
twine upload --repository testpypi dist/*

# Upload para PyPI
twine upload dist/*
```

### Versionamento
O projeto usa versionamento semântico (SemVer):
- `MAJOR.MINOR.PATCH`
- Exemplo: `0.1.0` → `0.1.1` → `0.2.0` → `1.0.0`

```bash
# Atualizar versão
bump2version patch  # 0.1.0 → 0.1.1
bump2version minor  # 0.1.1 → 0.2.0
bump2version major  # 0.2.0 → 1.0.0
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação
```python
# Problema: API key inválida ou ausente
# Solução:
client = EvolutionClient(api_key="sua-chave-correta")
# ou configure no .env
```

#### 2. Instância Não Conectada
```python
# Problema: Tentar enviar mensagem sem conectar WhatsApp
# Solução:
status = client.instance.connection_state("minha-instancia")
if status.get("state") != "open":
    qr = client.instance.connect("minha-instancia")
    print("Escaneie o QR code:", qr.qr_code_base64)
```

#### 3. Rate Limiting
```python
# Problema: Muitas requests por segundo
# Solução: Implementar retry com backoff
import time
from pyevolution.exceptions import RateLimitError

try:
    response = client.messages.send_text(...)
except RateLimitError as e:
    time.sleep(e.retry_after or 60)
    response = client.messages.send_text(...)  # Retry
```

#### 4. Timeout
```python
# Problema: Requests muito lentas
# Solução: Aumentar timeout
client = EvolutionClient(timeout=60.0)
```

### Debug Mode
```python
# Ativar logs detalhados
client = EvolutionClient(debug=True)

# Ou via environment
export EVOLUTION_DEBUG=true
```

## 🚀 Desenvolvimento

### Setup do Ambiente
```bash
# Clonar repositório
git clone https://github.com/lpcoutinho/pyevolution.git
cd pyevolution

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Instalar pre-commit hooks
pre-commit install
```

### Comandos Úteis
```bash
# Formatação de código
black pyevolution tests examples

# Linting
ruff check pyevolution tests examples

# Type checking
mypy pyevolution

# Executar todos os checks
pre-commit run --all-files

# Executar servidor de desenvolvimento da documentação
mkdocs serve
```

### Contribuição
1. Fork do repositório
2. Criar branch para feature (`git checkout -b feature/nova-funcionalidade`)
3. Fazer commits com mensagens descritivas
4. Executar testes e linting
5. Push para o branch (`git push origin feature/nova-funcionalidade`)
6. Abrir Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🤝 Suporte

- **GitHub Issues**: https://github.com/lpcoutinho/pyevolutionapi/issues
- **Discussões**: https://github.com/lpcoutinho/pyevolutionapi/discussions
- **Email**: your.email@example.com

## 📚 Recursos Adicionais

- [Evolution API Documentation](https://doc.evolution-api.com/)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [httpx Documentation](https://www.python-httpx.org/)

---

**PyEvolutionAPI** - Simplificando a integração com WhatsApp através da Evolution API 🚀