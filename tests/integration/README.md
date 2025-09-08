# Testes de Integração - PyEvolution API

Este diretório contém testes de integração que validam a biblioteca PyEvolution com uma instância **real** da Evolution API.

## 🎯 Propósito

Os testes de integração foram criados especificamente para validar as correções de validação Pydantic:

1. ✅ **Status "connecting"** é aceito pelo enum `InstanceStatus`
2. ✅ **Campo qrcode** aceita tipos mistos (`Dict[str, Any]`) não apenas strings
3. ✅ **Respostas reais da API** são parseadas sem `ValidationError`

## 🚀 Configuração Rápida

### 1. Configure a Evolution API
```bash
# Certifique-se que a Evolution API está rodando
# Normalmente em: http://localhost:8080
```

### 2. Configure credenciais
```bash
# Copie o arquivo de exemplo
cp .env.integration.example .env.integration

# Edite e configure suas credenciais
nano .env.integration
```

### 3. Execute os testes
```bash
# Método recomendado (script helper)
python run_integration_tests.py

# Ou diretamente com pytest
pytest tests/integration/ -v -m integration
```

## 📋 Tipos de Teste

### 🏃 Testes Rápidos (Recomendado)
```bash
python run_integration_tests.py --quick
```
- Cria/deleta instâncias automaticamente
- Valida parsing de respostas reais
- Não requer interação manual
- ⏱️ **~30-60 segundos**

### 🔄 Testes Normais
```bash
python run_integration_tests.py
```
- Inclui testes de ciclo de vida de instâncias
- Alguns testes podem ser mais lentos
- ⏱️ **~2-5 minutos**

### 🌐 Todos os Testes
```bash
python run_integration_tests.py --all
```
- **⚠️ ATENÇÃO:** Inclui testes que requerem escaneamento manual de QR code
- Use apenas quando necessário para testes completos
- ⏱️ **~5-15 minutos** (dependendo da interação manual)

## 🧪 Testes Implementados

### `TestRealInstanceCreation`
- ✅ Cria instâncias reais na Evolution API
- ✅ Valida que status "connecting" é aceito
- ✅ Verifica parsing de campo qrcode com tipos mistos
- ✅ Testa estados de conexão válidos

### `TestRealAPIResponseParsing`
- ✅ Testa parsing de `fetch_instances()` com instâncias reais
- ✅ Valida endpoints múltiplos sem erros de validação
- ✅ Verifica casos extremos de parsing

### `TestWithConnectedInstance`
- ⚠️ **Requer QR escaneado manualmente**
- ✅ Testa instâncias completamente conectadas
- 🔒 Pulado por padrão (use `--all` para incluir)

## 🔧 Configuração Detalhada

### Arquivo .env.integration
```bash
# Obrigatórias
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-api-aqui

# Opcionais
EVOLUTION_TEST_INSTANCE=pytest-integration
EVOLUTION_DEBUG=true
EVOLUTION_REQUEST_TIMEOUT=60
```

### Obter API Key
1. Acesse o manager da Evolution API (geralmente `http://localhost:8080/manager`)
2. Faça login ou crie uma conta
3. Copie sua API key
4. Configure no `.env.integration`

## 📊 Interpretando Resultados

### ✅ Sucesso Completo
```
=================== 8 passed in 45.2s ===================
🎉 Testes de integração concluídos com sucesso!
✅ As correções de validação Pydantic estão funcionando!
```

### ⚠️ Falhas Esperadas
Alguns falhas são esperadas e OK:
- `⚠️ Connect falhou (ok para este teste)` - Limitação da API
- `⚠️ Restart falhou (ok para este teste)` - Instância pode não existir

### ❌ Falhas Críticas
Estas indicam problemas reais:
- `ValidationError` ou `Pydantic` no log de erro
- `❌ Erro de validação Pydantic`
- Falha na criação básica de instâncias

## 🎯 Validações Específicas das Correções

Os testes validam especificamente que:

```python
# 1. Status "connecting" é aceito
assert instance.status == InstanceStatus.CONNECTING  # ✅ Funcionava ❌ antes

# 2. QRcode aceita tipos mistos
qrcode = {"count": 0, "base64": "...", "valid": True}  # ✅ Funcionava ❌ antes
instance = Instance(qrcode=qrcode)  # Sem ValidationError

# 3. Parsing de respostas reais funciona
response = real_client.instance.create(...)  # ✅ Sem ValidationError
```

## 🚨 Troubleshooting

### Erro: "Evolution API não está acessível"
```bash
# Verifique se está rodando
curl http://localhost:8080/health

# Verifique logs da Evolution API
# Ajuste EVOLUTION_BASE_URL se necessário
```

### Erro: "EVOLUTION_API_KEY não configurado"
```bash
# Configure no arquivo .env.integration
echo "EVOLUTION_API_KEY=sua-chave-aqui" >> .env.integration
```

### Timeout nos testes
```bash
# Aumente timeout no .env.integration
echo "EVOLUTION_REQUEST_TIMEOUT=120" >> .env.integration
```

### ValidationError ainda ocorre
Se ainda há `ValidationError` após as correções:
1. Verifique que está usando a versão correta da biblioteca
2. Reinstale: `pip install -e .`
3. Execute testes unitários primeiro: `pytest tests/unit/test_instance_models.py`

## 🔍 Debug e Logs

### Habilitar debug completo
```bash
# No .env.integration
EVOLUTION_DEBUG=true
EVOLUTION_LOG_LEVEL=DEBUG
```

### Ver requests HTTP
```bash
# Execute com debug verbose
pytest tests/integration/ -v -s --tb=long -m integration
```

### Salvar logs
```bash
python run_integration_tests.py 2>&1 | tee integration_test.log
```

## 📚 Referências

- [Evolution API Documentation](https://doc.evolution-api.com/)
- [PyTest Integration Testing](https://docs.pytest.org/en/stable/)
- [Pydantic Validation](https://docs.pydantic.dev/)

---

> 💡 **Dica:** Execute `python run_integration_tests.py --setup` para ver instruções detalhadas de configuração.
