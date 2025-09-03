# 🚀 Release Checklist - PyEvolutionAPI

## ✅ Pré-Release

### Código
- [ ] Todos os testes passando (`pytest`)
- [ ] Cobertura de testes >= 65%
- [ ] Linting ok (`black`, `ruff`)
- [ ] Type hints verificados
- [ ] Documentação atualizada

### Versionamento
- [ ] Version bump no `pyproject.toml`
- [ ] CHANGELOG.md atualizado (se mantiver)
- [ ] README badges atualizadas
- [ ] Exemplos testados e funcionando

### Build Local
- [ ] `python -m build` executa sem erros
- [ ] `twine check dist/*` passa
- [ ] Instalação local funciona: `pip install dist/*.whl`
- [ ] Import funciona: `python -c "from pyevolutionapi import EvolutionClient"`

## 🔄 Processo de Release

### Opção A: Via Git Tag (Recomendado)
```bash
# 1. Commit todas as mudanças
git add .
git commit -m "chore: bump version to X.Y.Z"

# 2. Criar e push tag
git tag vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z

# 3. GitHub Actions fará o resto automaticamente
```

### Opção B: Via GitHub UI
1. Ir para Releases no GitHub
2. "Create a new release"
3. Tag: `vX.Y.Z`
4. Title: `PyEvolution vX.Y.Z`
5. Descrever mudanças
6. "Publish release"

## 📊 Monitoramento

### GitHub Actions
- [ ] Build Distribution ✅
- [ ] Test Installation ✅
- [ ] Publish to PyPI ✅
- [ ] Create GitHub Release ✅

### Verificação PyPI
- [ ] Pacote disponível em https://pypi.org/project/pyevolutionapi/
- [ ] Versão correta publicada
- [ ] Metadados corretos
- [ ] Download e instalação: `pip install pyevolutionapi`

### Pós-Release
- [ ] Testar instalação em ambiente limpo
- [ ] Verificar documentação online
- [ ] Anunciar release (se aplicável)
- [ ] Atualizar exemplos/demos

## 🐛 Troubleshooting

### Erro: "Version already exists"
- Não é possível republicar a mesma versão
- Sempre incremente a versão no pyproject.toml

### Erro: GitHub Actions falha
- Verificar logs em Actions tab
- Verificar environments configurados
- Verificar permissões: `id-token: write`

### Erro: Import não funciona
- Verificar se o build incluiu todos os arquivos
- Verificar dependências no pyproject.toml
- Testar em venv limpo

## 📚 Links Rápidos

- [PyPI Package](https://pypi.org/project/pyevolutionapi/)
- [GitHub Releases](https://github.com/lpcoutinho/pyevolutionapi/releases)
- [GitHub Actions](https://github.com/lpcoutinho/pyevolutionapi/actions)
- [Documentation](https://lpcoutinho.github.io/pyevolutionapi/)

---

**Próximo Release:** v0.2.0 🎯
