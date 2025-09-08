# 📱 Guia de Teste de Conexão WhatsApp

Este guia ensina como usar o teste interativo de conexão WhatsApp que exibe QR codes diretamente no terminal.

## 🚀 Instalação Rápida

### 1. Instalar Dependências
```bash
# Dependências necessárias para QR code
pip install -r requirements-qr.txt

# Ou instalação manual
pip install qrcode[pil]
```

### 2. Configurar Evolution API
```bash
# Copie o arquivo de exemplo
cp .env.integration.example .env.integration

# Configure suas credenciais no .env.integration
nano .env.integration
```

### 3. Executar Teste
```bash
# Teste básico
python test_whatsapp_connection.py

# Ou com opções avançadas
python test_whatsapp_connection.py --name meu-whatsapp --timeout 180
```

## 📋 Comandos Disponíveis

### **Teste Básico**
```bash
python test_whatsapp_connection.py
```
- Cria instância automática
- Exibe QR code no terminal
- Monitora conexão por 5 minutos
- Remove instância automaticamente

### **Teste Personalizado**
```bash
# Nome da instância personalizado
python test_whatsapp_connection.py --name "meu-bot-whatsapp"

# Timeout personalizado (3 minutos)
python test_whatsapp_connection.py --timeout 180

# Manter instância após teste
python test_whatsapp_connection.py --no-cleanup

# Verificar dependências
python test_whatsapp_connection.py --check-deps
```

### **Gerenciamento de Instâncias**
```bash
# Listar instâncias existentes
python cleanup_instances.py --list

# Remover instâncias de teste
python cleanup_instances.py --clean-test
```

## 🎯 Como Funciona o Teste

### **1. Criação da Instância**
```
============================================================
 CRIANDO INSTÂNCIA WHATSAPP
============================================================

📱 Criando instância: whatsapp-test-1725821234
✅ Instância criada com sucesso!
📋 Status: connecting
📋 ID: abc123-def456-ghi789
```

### **2. Exibição do QR Code**
```
============================================================
 QR CODE PARA CONEXÃO WHATSAPP
============================================================

📱 Escaneie este QR code com seu WhatsApp:

█▀▀▀▀▀█ ▀▀ █▀ █▀▀▀▀▀█
█ ███ █ ▀▀█ ▀  █ ███ █
█ ▀▀▀ █ █▀▄█▀▄ █ ▀▀▀ █
▀▀▀▀▀▀▀ ▀▄█▄▀▄ ▀▀▀▀▀▀▀
▀██▀▄▀▀▀▀█▄ ▄▀ ▀█▄▀█▀▀
 ▀ ▄▀▄▀▄▄██▀▄▄▀▄▄▀▄ ▄▀
▀▀▀▀▀▀▀ ▀   ▀ █▀▀▀▀▀█
█▀▀▀▀▀█   ▀▄▄▄ █ ███ █
█ ███ █ ▀██▀▄▄ █ ▀▀▀ █
█ ▀▀▀ █ ▀▀▄ ▄▄▄▀▀▀▀▀▀▀
▀▀▀▀▀▀▀ ▀▀▀    ▀▀▀▀▀▀▀

📱 Como conectar:
1. Abra o WhatsApp no seu celular
2. Toque em ⋮ (três pontos) > Dispositivos conectados
3. Toque em 'Conectar um dispositivo'
4. Escaneie o QR code acima
```

### **3. Monitoramento em Tempo Real**
```
============================================================
 MONITORANDO CONEXÃO
============================================================

⏱️ Aguardando conexão por até 5 minutos...
⏹️ Pressione Ctrl+C para cancelar

🔍 Verificando conexão... (tentativa 1, restam 4:57)
🔄 Status: connecting (aguardando QR scan)
🔍 Verificando conexão.. (tentativa 2, restam 4:54)
📊 Status: connecting
🔍 Verificando conexão... (tentativa 3, restam 4:51)
🎉 WHATSAPP CONECTADO COM SUCESSO!
👤 Nome: Seu Nome
📞 Número: 5511999999999
```

### **4. Resultado Final**
```
============================================================
 TESTE CONCLUÍDO COM SUCESSO
============================================================

✅ WhatsApp conectado à Evolution API!
🎯 Todas as correções Pydantic validadas!

============================================================
 LIMPEZA
============================================================

🗑️ Instância removida: whatsapp-test-1725821234
```

## 🔧 Configuração Avançada

### **Arquivo .env.integration**
```bash
# Configuração da Evolution API
EVOLUTION_BASE_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-api-aqui

# Configurações opcionais
EVOLUTION_DEBUG=false
EVOLUTION_REQUEST_TIMEOUT=60
```

### **Opções do Script**
```bash
# Ajuda completa
python test_whatsapp_connection.py --help

# Verificar se tudo está configurado
python test_whatsapp_connection.py --check-deps
```

## ⚠️ Troubleshooting

### **Problema: QR Code não aparece**
```bash
# Instale as dependências
pip install qrcode[pil]

# Ou verifique instalação
python test_whatsapp_connection.py --check-deps
```

### **Problema: Erro de autenticação**
```bash
# Verifique API key no .env.integration
echo $EVOLUTION_API_KEY

# Teste conexão com Evolution API
curl -H "apikey: sua-chave" http://localhost:8080/health
```

### **Problema: Timeout de conexão**
```bash
# Aumente o timeout
python test_whatsapp_connection.py --timeout 600  # 10 minutos

# Ou verifique se QR está válido
python test_whatsapp_connection.py --no-cleanup
python cleanup_instances.py --list
```

### **Problema: Instâncias acumuladas**
```bash
# Liste instâncias
python cleanup_instances.py --list

# Remove instâncias de teste
python cleanup_instances.py --clean-test
```

## 🎯 Recursos do Teste

### ✅ **Validações das Correções Pydantic**
- Status "connecting" aceito sem ValidationError
- QR code com tipos mistos (`{"count": 0}`) parseado
- Instâncias reais da API processadas corretamente

### 🔧 **Funcionalidades**
- **QR Code ASCII** exibido diretamente no terminal
- **Monitoramento em tempo real** da conexão
- **Cores e formatação** para melhor experiência
- **Limpeza automática** das instâncias
- **Timeout configurável** e cancelamento manual
- **Logs detalhados** do processo

### 🛡️ **Segurança**
- Remove instâncias automaticamente
- Não armazena credenciais
- Suporte a Ctrl+C para cancelamento
- Validação de dependências

## 💡 Dicas

1. **Mantenha o WhatsApp aberto** durante o teste
2. **QR codes expiram** - teste logo após aparecimento
3. **Use timeout menor** para testes rápidos
4. **Mantenha Evolution API rodando** durante o teste
5. **Configure logs em debug** se houver problemas

## 🚀 Próximos Passos

Após conectar com sucesso:

1. **Teste envio de mensagens** com a instância conectada
2. **Explore outras funcionalidades** da PyEvolution API
3. **Integre em seus projetos** com confiança
4. **Configure webhooks** para receber mensagens

---

**🎉 Agora você pode conectar WhatsApp real à Evolution API com facilidade!**
