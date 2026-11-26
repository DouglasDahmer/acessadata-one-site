# AcessaData-ONE — Procedimento de manutenção e publicação

**Escopo:** repositório público `DouglasDahmer/acessadata-one-site` e projeto
Cloudflare Pages Direct Upload `acessadata-one`.

## 1. Separação dos ambientes

- **Fonte pública Git:** branch `main` do repositório acima, com histórico iniciado
  no commit `b79ce6ec4c81c1f71b6eabd9bb836f9886548e25`.
- **Clone histórico local:** branch `site-ap-11-integracao`, commit
  `e3e10a24a24d657c7e7f6828ddd13f95691d3e64`. Foi preservado isolado,
  com histórico de dois commits não enviado ao GitHub.
- **Production:** https://acessadata-one.com.br/ — implantação independente
  do GitHub. Push de código não faz deploy automático.
- **Preview:** usar uma implantação de homologação distinta da Production.

**Nunca faça `git push --force`, `git reset --hard`, `git clean` ou merge de
históricos sem validação explícita de risco e backup.** Para alterações futuras,
crie uma branch de desenvolvimento a partir da `main` pública, de preferência
num clone isolado. Não substitua o histórico público pelo histórico local antigo.

## 2. Fluxo de alterações na fonte

1. Consulte a branch `main`, confirme o HEAD esperado e crie uma branch nova.
2. Verifique `git status`; não misture alterações de outros projetos.
3. Modifique fontes e documentação; preserve arquivos de terceiros e registre
   origem/licenças ao atualizá-los.
4. Execute o build **somente com `dist/` ausente ou vazia**:

   ```powershell
   python -B build.py
   if ($LASTEXITCODE -ne 0) { throw "BUILD_FALHOU" }
   python -B -m unittest discover -s . -p "test_*.py" -v
   if ($LASTEXITCODE -ne 0) { throw "TESTES_FALHARAM" }
   ```

5. Avalie `git diff --check`, os testes, o conteúdo de `dist/`, os hyperlinks,
   os dados publicados, a política CSP e a acessibilidade em navegador.
6. Gere manifesto de hashes do **novo** pacote, com data, origem e commit.
   Não reutilize hashes antigos para afirmar integridade de uma versão alterada.
7. Revise os arquivos staged (`git diff --cached`) e o histórico antes de
   disponibilizar dados ou fontes em repositório público.
8. Efetue o commit e faça push somente após revisão. A branch `main` deve ser
   atualizada por integração controlada, sem sobrescrever histórico.

## 3. Implantação no Cloudflare Pages

1. Faça backup do pacote e registre qual deployment de Production está ativo.
2. Produza o ZIP **somente** a partir de uma distribuição nova, revisada e
   integralmente verificada, com a estrutura HTML na raiz do arquivo ZIP.
3. Publique primeiro em **Preview**, conferindo renderização, assets, links,
   responsividade, tabela acessível e headers.
4. Após aprovação explícita da nova versão, escolha **Production** no projeto
   `acessadata-one` e realize **Direct Upload** do ZIP aprovado.
5. Verifique a página inicial, `/storytelling/` e o relatório Quarto, além
   dos redirecionamentos históricos, CSP, `nosniff` e ausência de `noindex`
   em Production. Compare SHA-256 dos recursos servidos com o manifesto
   daquela versão.
6. Se houver regressão, siga o fluxo de rollback permitido pelo Cloudflare
   para um deployment anterior validado; documente a alteração e faça nova
   auditoria HTTP. Não presuma rollback automático.

**Último baseline documentado (2026-11-23):** pacote com 49 arquivos,
47 recursos HTTPS conferidos, 5 redirecionamentos 301 e políticas de
segurança nas três páginas. O baseline descreve aquele deployment, não um
controle contínuo nem a aprovação de versões futuras.

## 4. Terceiros, dados e segurança

- Revisar `LICENCAS_TERCEIROS.md` antes de atualizar bibliotecas ou republicar
  assets. Pendências conhecidas: versão do Quarto gerador, correspondência
  exata da build Tippy.js, componentes/transitivas e publicação dos avisos
  legais no artefato distribuído. Preservar textos de copyright e licenças.
- Não incluir `.env`, chaves privadas, tokens, microdados pessoais, backups,
  dumps, temporários ou `dist/` no histórico Git.
- Conferir se arquivos CSV/JSON contêm exclusivamente dados permitidos para
  publicação; agregação por si só não elimina todo risco de reidentificação.
- Credenciais não devem ser copiadas para relatórios, commits ou mensagens.
- Não declarar certificação WCAG, auditoria independente dos microdados ou
  comprovação causal sem evidência específica.

## 5. Registro de cada release

Guardar fora da fonte principal: identificação do commit e da branch, saída
completa dos testes, manifesto SHA-256, ZIP, parecer de Preview, identificador
de Production, verificações HTTP e plano de rollback. Associar o registro à
versão e à data efetivamente implantadas.
