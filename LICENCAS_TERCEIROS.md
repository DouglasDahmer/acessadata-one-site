# Avisos de terceiros — AcessaData-ONE

Este documento identifica bibliotecas redistribuidas em `publicacao_extras/`.
Os arquivos em `licencas_terceiros/` sao copias integrais das licencas
obtidas dos repositorios oficiais ou do pacote npm da versao indicada.
Seu conteudo foi verificado por SHA-1 de objeto Git ou SRI SHA-512 npm.

## Componentes e textos legais

| Componente | Licenca de referencia | Texto incluido | Fonte |
|---|---|---|---|
| D3 7.9.0 | ISC | `licencas_terceiros/d3-7.9.0-LICENSE.txt` | https://github.com/d3/d3/blob/v7.9.0/LICENSE |
| Bootstrap 5.3.1 | MIT/atribuicoes conforme fonte | `licencas_terceiros/bootstrap-5.3.1-LICENSE.txt` | https://github.com/twbs/bootstrap/blob/v5.3.1/LICENSE |
| Bootstrap Icons 1.13.1 | MIT/atribuicoes conforme fonte | `licencas_terceiros/bootstrap-icons-1.13.1-LICENSE.txt` | https://github.com/twbs/icons/blob/v1.13.1/LICENSE |
| Clipboard.js 2.0.11 | MIT/atribuicoes conforme fonte | `licencas_terceiros/clipboard-2.0.11-LICENSE.txt` | https://github.com/zenorocha/clipboard.js/blob/v2.0.11/LICENSE |
| AnchorJS 5.0.0 | MIT/atribuicoes conforme fonte | `licencas_terceiros/anchorjs-5.0.0-LICENSE.txt` | https://github.com/bryanbraun/anchorjs/blob/5.0.0/LICENSE |
| Tippy.js 6.3.7 (referencia a confirmar contra build Quarto) | MIT/atribuicoes conforme fonte | `licencas_terceiros/tippy-6.3.7-LICENSE.txt` | https://github.com/atomiks/tippyjs/blob/v6.3.7/LICENSE |
| Quarto CLI (COPYRIGHT de referencia; versao do gerador nao determinada) | MIT/atribuicoes conforme fonte | `licencas_terceiros/quarto-cli-COPYRIGHT-referencia.txt` | https://github.com/quarto-dev/quarto-cli/blob/main/COPYRIGHT |
| Popper @popperjs/core 2.11.7 | MIT/atribuicoes conforme fonte | `licencas_terceiros/popper-2.11.7-LICENSE.txt` | https://registry.npmjs.org/@popperjs/core/-/core-2.11.7.tgz [package/LICENSE.md; metadata npm 2.11.7] |

## Limites desta documentacao

- Os 35 recursos em `publicacao_extras/` permanecem byte a byte identicos.
- `quarto.js` e outros assets do Quarto podem incorporar dependencias
  adicionais; este inventario NAO declara cobertura juridica exaustiva.
- A versao do Quarto que gerou o HTML nao foi determinada neste controle.
- A versao exata de Tippy.js embutida no Quarto nao foi comprovada:
  o arquivo Tippy 6.3.7 e referencia upstream, nao uma correspondencia
  binaria demonstrada do JS minificado publicado.
- As versoes de D3, Bootstrap, Bootstrap Icons, Clipboard.js, AnchorJS
  e Popper correspondem a indicios de versao identificados no conteudo.
- D3 pode conter submodulos com creditos/licencas proprios; revisar
  avisos de subdependencias para uma conformidade completa.
- Os textos legais de licenca nao substituem uma revisao juridica.
- Este arquivo pertence ao repositório FONTE; nao foi incluido no pacote
  ZIP de Production e nao declara que os avisos estejam publicados no site.

Referencia do Quarto: https://quarto.org/license.html
Pagina institucional: https://acessadata-one.com.br/
