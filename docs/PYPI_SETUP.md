# 📦 Guia de Configuração do PyPI para PyEvolutionAPI

## 📝 Pré-requisitos

### 1. Criar Conta no PyPI
1. Acesse [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Crie uma conta com email válido
3. Confirme o email de verificação
4. (Opcional) Crie conta no [Test PyPI](https://test.pypi.org/account/register/) para testes

### 2. Habilitar Two-Factor Authentication (2FA)
1. Acesse Account Settings no PyPI
2. Vá para "Two factor authentication (2FA)"
3. Configure usando um app como Google Authenticator ou Authy
4. Guarde os códigos de recuperação

## 🔑 Configuração de API Tokens

### Para PyPI Principal
1. Acesse [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Clique em "Add API token"
3. Nome: `pyevolutionapi-github-actions`
4. Scope: "Entire account" (primeira vez) ou "Project: pyevolutionapi" (após primeira publicação)
5. Copie e guarde o token (começa com `pypi-`)

### Para Test PyPI
1. Acesse [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
2. Siga os mesmos passos acima
3. Token começará com `pypi-` também

## 🔧 Configuração no GitHub

### 1. Configurar Environments no GitHub

#### Environment: `pypi`
1. Vá para Settings → Environments no seu repositório
2. Clique em "New environment"
3. Nome: `pypi`
4. Configure:
   - ✅ Required reviewers (opcional, para aprovar releases)
   - ✅ Wait timer: 0-30 minutos (opcional)
   - Deployment branches: `Selected branches`
   - Add rule: `v*` (apenas tags de versão)

#### Environment: `test-pypi`
1. Crie outro environment chamado `test-pypi`
2. Configuração similar, mas sem restrições de branch

### 2. Configurar Trusted Publishing (Recomendado)

O PyPI agora suporta "Trusted Publishing" com GitHub Actions, que é mais seguro que usar tokens.

#### No PyPI:
1. Acesse [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
2. Adicione um novo publisher:
   - Publisher: GitHub
   - Repository owner: `lpcoutinho`
   - Repository name: `pyevolutionapi`
   - Workflow name: `publish.yml`
   - Environment: `pypi`

#### No Test PyPI:
1. Mesma configuração em [https://test.pypi.org/manage/account/publishing/](https://test.pypi.org/manage/account/publishing/)
2. Environment: `test-pypi`

## 📊 Verificar Configuração do Projeto

### pyproject.toml
Verifique se tem as informações corretas:

```toml
[project]
name = "pyevolutionapi"
version = "0.1.0"  # Atualize para cada release
description = "Python client for Evolution API - WhatsApp integration made simple"
readme = "README.md"
authors = [
    { name = "Luiz Paulo Coutinho", email = "seu-email-real@example.com" }
]
license = { text = "MIT" }
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Communications :: Chat",
]
requires-python = ">=3.8"
dependencies = [
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "typing-extensions>=4.5.0;python_version<'3.10'",
]

[project.urls]
Homepage = "https://github.com/lpcoutinho/pyevolutionapi"
Documentation = "https://lpcoutinho.github.io/pyevolutionapi/"
Repository = "https://github.com/lpcoutinho/pyevolutionapi"
Issues = "https://github.com/lpcoutinho/pyevolutionapi/issues"
```

## 🚀 Processo de Release

### 1. Teste Local

```bash
# Instalar ferramentas de build
pip install build twine

# Fazer build do pacote
python -m build

# Verificar o pacote
twine check dist/*

# Testar instalação local
pip install dist/*.whl

# Testar importação
python -c "from pyevolutionapi import EvolutionClient; print('OK')"
```

### 2. Teste no Test PyPI (Opcional mas Recomendado)

```bash
# Upload para Test PyPI
twine upload --repository testpypi dist/*

# Instalar do Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyevolutionapi

# Testar
python -c "from pyevolutionapi import EvolutionClient; print('Test PyPI OK')"
```

### 3. Release Automatizado via GitHub Actions

#### Opção A: Via Git Tag (Recomendado)
```bash
# Atualizar versão no pyproject.toml
# Commit as mudanças
git add pyproject.toml
git commit -m "chore: bump version to 0.1.1"

# Criar tag
git tag v0.1.1 -m "Release v0.1.1"

# Push tag (isso dispara o workflow)
git push origin v0.1.1
```

#### Opção B: Via GitHub Release UI
1. Vá para Releases no GitHub
2. Click "Create a new release"
3. Create new tag: `v0.1.1`
4. Release title: `v0.1.1`
5. Descreva as mudanças
6. ✅ Set as latest release
7. Publish release

### 4. Monitorar o Deploy

1. Acesse Actions no GitHub
2. Veja o workflow "Publish to PyPI" em execução
3. Etapas:
   - ✅ Build Distribution
   - ✅ Test Installation (Python 3.8, 3.11, 3.12)
   - ✅ Publish to PyPI (aguarda approval se configurado)
   - ✅ Create GitHub Release

### 5. Verificar no PyPI

Após publicação bem-sucedida:
1. Acesse [https://pypi.org/project/pyevolutionapi/](https://pypi.org/project/pyevolutionapi/)
2. Verifique a versão publicada
3. Teste instalação: `pip install pyevolutionapi`

## 📋 Checklist Pré-Release

- [ ] Testes passando (`pytest`)
- [ ] Código formatado (`black`, `ruff`)
- [ ] Documentação atualizada
- [ ] Version bump no `pyproject.toml`
- [ ] CHANGELOG.md atualizado (se mantiver um)
- [ ] README.md badges atualizadas
- [ ] Exemplos funcionando
- [ ] Build local testado
- [ ] Test PyPI testado (primeira vez)

## 🐛 Troubleshooting

### Erro: "No matching distribution"
- Verifique se o nome do pacote está correto no pyproject.toml
- Certifique-se que o build foi executado: `python -m build`

### Erro: "Invalid or non-existent authentication"
- Verifique o Trusted Publishing configuration
- Ou configure secret `PYPI_API_TOKEN` no GitHub

### Erro: "Version already exists"
- Você não pode republicar a mesma versão
- Sempre incremente a versão no pyproject.toml

### Erro no GitHub Actions
- Verifique os logs detalhados em Actions
- Certifique-se que os environments estão configurados
- Verifique as permissões: `id-token: write`

## 🔒 Segurança

1. **Nunca commite tokens** no código
2. Use **Trusted Publishing** ao invés de tokens quando possível
3. Habilite **2FA** em todas as contas
4. Revise dependências antes de cada release
5. Use **environments** do GitHub para controlar deploys

## 📚 Links Úteis

- [PyPI Official Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [GitHub Actions PyPI Publish](https://github.com/pypa/gh-action-pypi-publish)
- [Test PyPI](https://test.pypi.org/)

---

## 🎯 Próximos Passos

1. **Configure sua conta PyPI** com 2FA
2. **Configure Trusted Publishing** no PyPI
3. **Configure os Environments** no GitHub
4. **Faça um release de teste** para o Test PyPI
5. **Publique sua primeira versão** oficial!

Para fazer o primeiro release oficial:

```bash
# 1. Garanta que tudo está commitado e pushed
git status

# 2. Crie e push a tag
git tag v0.1.0 -m "Initial release"
git push origin v0.1.0

# 3. Monitore em GitHub Actions
# 4. Celebre! 🎉
```
