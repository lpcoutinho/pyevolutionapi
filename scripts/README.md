# Scripts de Desenvolvimento

Esta pasta contém scripts utilitários para desenvolvimento e testes da biblioteca PyEvolution.

## 📋 Scripts Disponíveis

### `test_whatsapp_connection.py`
Script interativo para testar conexão WhatsApp com Evolution API em tempo real.

**Funcionalidades:**
- Cria instância na Evolution API
- Exibe QR code visualmente no terminal
- Monitora conexão em tempo real
- Limpeza automática de instâncias de teste

**Uso:**
```bash
# Teste básico
python scripts/test_whatsapp_connection.py

# Com nome personalizado
python scripts/test_whatsapp_connection.py --name meu-teste

# Timeout customizado (3 minutos)
python scripts/test_whatsapp_connection.py --timeout 180

# Manter instância após teste
python scripts/test_whatsapp_connection.py --no-cleanup

# Verificar dependências
python scripts/test_whatsapp_connection.py --check-deps
```

**Dependências:**
```bash
pip install qrcode[pil] python-dotenv
```

**Configuração:**
Crie `.env.integration` com suas credenciais:
```env
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=your-api-key
```

## 🔧 Como Usar

1. Configure suas credenciais da Evolution API
2. Instale dependências necessárias
3. Execute o script desejado
4. Siga as instruções na tela

## ⚠️ Importante

- Scripts desta pasta são para desenvolvimento e teste
- Não são incluídos na distribuição do pacote
- Podem requerer Evolution API rodando localmente
- Use apenas em ambiente de desenvolvimento

## 🚀 Contribuição

Para adicionar novos scripts:

1. Documente seu propósito e uso
2. Adicione tratamento de erros adequado
3. Include exemplo de uso neste README
4. Use padrões de código da biblioteca
