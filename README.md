# AcessaData-ONE v4.7 — Interface simplificada

Veja `ALTERACOES_v4_7.md` para as mudanças, instruções e validações.

## Correcao v4.5.1 - Suite de testes portavel

Os testes 48, 49 e 50 da v4.5 exigiam acidentalmente a biblioteca Beautiful Soup 4 (bs4), nao incluida como dependencia do projeto. Agora os testes usam somente html.parser da biblioteca padrao Python. Os arquivos do site, imagens, dados e mapa dos 17 pontos da arvore permanecem iguais a v4.5. Executar: `python build.py` e `python -m unittest test_site -v`.

# AcessaData-ONE — Site v4.3, refinamento da árvore interativa

A página mantém a árvore do logotipo original do usuário. Seus **17 círculos são links**.
No desktop, **passar o mouse ou focar com Tab** mostra título, descrição e indicação de ação;
**clicar ou pressionar Enter** leva diretamente à seção correspondente.
No celular, a imagem original continua visível, acompanhada de **17 links com nomes legíveis**;
isso evita exigir toques em pontos muito próximos entre si.

## Novidades na v4.2

- Janela de descrição com transição suave no hover e foco.
- Ajuste horizontal automático das descrições junto às bordas do navegador.
- Tecla **Esc** fecha a descrição mantendo o foco no link; **Tab** muda de círculo e **Enter** abre a seção.
- Respeita a preferência do sistema por **movimento reduzido**, inclusive rolagem da página.
- Sem coleta de dados ou dependências externas: o site continua totalmente estático.
- A imagem da árvore, as coordenadas dos 17 pontos e os destinos foram preservados.


## Iniciar no Windows (PowerShell)

1. Descompacte `AcessaDataONE_Site_Arvore_Interativa_v4_3_Python.zip` na sua Área de Trabalho.
2. Abra o PowerShell. Execute:

```powershell
$desktop = [Environment]::GetFolderPath("Desktop")
Set-Location (Join-Path $desktop "AcessaDataONE_Website_Python_v4_3")
python .\build.py
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar o site." }
python -m unittest test_site -v
python -m http.server 8000 --bind 127.0.0.1 --directory .\dist
```

3. Abra http://127.0.0.1:8000/ **depois** que aparecer `Serving HTTP`.
4. Mantenha o terminal aberto. Para interromper use `Ctrl+C`.
5. Se preferir outra porta, substitua `8000` por `8080` nos comandos e na URL.

## Como atualizar o conteúdo

- `content/site.json` — textos, serviços, projetos e contatos.
- `content/mapa_circulos.json` — 17 rótulos e coordenadas do mapa de navegação.
- `assets/style.css` — estilo e responsividade.
- `assets/main.js` — aprimoramento opcional do painel de informações.
- `assets/arvore-original.webp` — **árvore verdadeira extraída do logo original de alta resolução**.
- `design/arvore-original-alta-resolucao.png` — referência de alta qualidade.

Depois de modificar arquivos de origem, rode `python build.py` novamente e atualize o navegador.

## Importante

- A árvore é a original do usuário, não uma imagem gerada automaticamente.
- Os links usam HTML nativo; funcionam sem JavaScript. A ajuda visual usa CSS no hover/foco.
- O mapeamento é aproximado e deve ser testado no navegador com diferentes tamanhos de tela.
- Nenhum dado de visitantes é coletado. A página de contato usa `mailto:`.
- A conformidade completa com WCAG 2.2 AA depende de avaliação formal adicional.
- Conteúdos de projetos não declaram lançamentos comerciais inexistentes.
- A identificação empresarial vigente é ACESSADATA-ONE INOVA SIMPLES (I.S.), CNPJ 69.899.726/0001-04, conforme Certificado de Inova Simples emitido em 30/10/2026.


## Novidade v4.2 — Fundador e contato

- Cartão Sobre com fotografia de Douglas H.S. Dahmer, enviada pelo usuário.
- Texto do perfil e contatos são HTML, não fazem parte de imagem estática: legíveis, selecionáveis e acessíveis.
- WhatsApp no cartão do fundador e na seção Contato: `https://wa.me/5551994313154`.
- Telefone no formato de discagem internacional e e-mail comercial já existente.
- Editar número em `content/site.json` (`phone_display` e `phone_e164`), depois executar `python build.py`.
- Fotografia: `assets/douglas-henrique-silveira-dahmer.webp` (fonte original enviada pelo fundador).
- ATENÇÃO: publicar o site disponibiliza publicamente foto e número de WhatsApp. Confirmar antes de publicar.
- A árvore original e seus 17 links não foram alterados.
- A qualidade da foto atual depende da imagem de origem (256×256 px); usar foto maior no futuro melhora nitidez em telas grandes.


## Novidade v4.3 — identidade visual reforçada

- Logo horizontal **original e preservado** passa a 310 px em desktop (em vez de 242 px), com altura de cabeçalho de 104 px.
- Cabeçalho usa navegação compacta a partir de 1090 px, evitando sobreposição da marca e do menu.
- Estilo de destaque usa `Bahnschrift` (com alternativas de sistema), que **aproxima** o lettering tecnológico da logomarca. A fonte exata da arte não foi identificada. Não há fontes distribuídas nem carregadas por terceiros.
- Fonte de leitura permanece Inter/Segoe UI/Arial para descrições, conteúdo e parágrafos.
- Títulos do hero, seções, cards e pop-ups da árvore recebem hierarquia tipográfica mais consistente.
- A árvore original, os 17 círculos, foto, contatos, navegação pelo teclado e respectivo mapa foram preservados.
- **Inspeção necessária:** após `python build.py`, verificar visualmente em Firefox (desktop e mobile) e aumentar o zoom até 200%; realizar auditoria WCAG 2.2 AA antes de declarar conformidade.
- Caso o servidor antigo esteja em execução, encerrar com `Ctrl+C` antes de iniciar esta versão; não apagar a pasta anterior.


## Novidade v4.3.1 — Tipografia de destaque inspirada no logotipo

- O chip **DATA · INNOVATION · TECHNOLOGY** usa Michroma, uma fonte aberta de aspecto geométrico similar à família visual Eurostile/Microgramma. A **fonte exata do logotipo NÃO foi identificada**: a marca é uma imagem com lettering desenhado.
- Títulos curtos de apresentação e os títulos dos balões dos círculos também recebem a identidade visual; parágrafos e instruções mantêm fonte de leitura.
- A versão consulta a folha de estilos pública do Google Fonts para carregar Michroma. Isso requer conexão com a internet e estabelece contato com um serviço externo; em uso local/offline, recorre automaticamente às fontes de sistema (Bahnschrift, Trebuchet MS). Para uso público com privacidade mais restrita, avaliar hospedagem própria licenciada da tipografia ou voltar ao fallback de sistema.
- Não há arquivos de fontes incluídos no pacote. A logomarca, a árvore original, os 17 links, a foto e os contatos foram preservados.
- Verificar visualmente o novo chip e a quebra de linha em Firefox no desktop e no celular; uma fonte semelhante não substitui a identificação tipográfica do logotipo.
- Diretório de instalação desta revisão: `AcessaDataONE_Website_Python_v4_3_1`.


## Novidade v4.4 — estudo de caso com dados agregados públicos

- A seção Projetos passa a oferecer **Explorar estudo de caso** para AcessaData-Health.
- Endereço legado (redirecionado): `estudo-acessadata-health-rs-2024.html`, com contagens de óbitos por sexo, idade e códigos CID-10, gráficos acompanhados de tabelas acessíveis, metodologia e limitações.
- Os valores são **agregados informados na execução anterior pelo desenvolvedor**. Este site NÃO reexecuta a ingestão original SIM 2024 nem autentica os arquivos brutos; publicar os scripts e hashes de insumos será uma etapa posterior.
- Conteúdo editável: `content/estudo_health_rs_2024.json`. Ao alterar resultados, revise fontes, métodos e validações, rode `python build.py` e `python -m unittest test_site -v`.
- A fonte pública oficial é o [SIM Mortalidade Geral 2024](https://dadosabertos.saude.gov.br/dataset/sim/resource/f0bdf83f-708e-4de9-9582-959055844ae9).
- Agregados no pacote de publicação: `dist/dados/acessadata-health-rs-2024-resumo.json` e `dist/dados/acessadata-health-rs-2024-top-cid.csv`. Nenhum dado individual de saúde é publicado.
- **Não calcular ou divulgar taxas de mortalidade com base apenas nessas contagens.** Demografia e denominadores precisam de auditoria adequada.
- A árvore do logotipo, todos os 17 círculos e respectivas posições, o cartão do fundador e o contato via WhatsApp permanecem preservados.
- Instalação local: extraia o ZIP no Desktop e execute `python build.py`, `python -m unittest test_site -v` e `python -m http.server 8000 --bind 127.0.0.1 --directory dist`.


## Novidade v4.5 — Usabilidade e clareza comercial

- A página inicial apresenta imediatamente o serviço oferecido e dois caminhos de ação claros: **Solicitar uma análise** e **Ver estudo de caso**.
- **Desktop:** seis links com nomes sempre visíveis ajudam a descobrir os destinos principais da árvore; os respectivos círculos recebem contornos suaves sem modificar o desenho original.
- **Celular:** seis destinos principais são exibidos primeiro. Os outros onze estão em um bloco nativo **`<details>`**, expansível com mouse, teclado ou toque.
- Cards de serviços agora apresentam o problema típico abordado, uma **entrega proposta** e um caminho até o contato. Não são promessas de resultados específicos nem relatos de contratos concluídos.
- A seção de contato orienta a não enviar informações sensíveis no primeiro contato; o site continua **sem banco de dados e sem formulário**.
- A **imagem original da árvore**, os 17 links e suas coordenadas, a foto do fundador, e-mail, WhatsApp e estudo de caso v4.4 continuam preservados.
- Testes automatizados cobrem os novos itens; ainda precisamos validar com pessoas reais e tecnologias assistivas antes de alegar conformidade WCAG 2.2 AA.
- Para executar, use a pasta `AcessaDataONE_Website_Python_v4_5`.


## v4.6 — cabeçalho essencial e árvore como navegação

- No topo da homepage: apenas logomarca original (link ao início) e botão **Entrar em contato**.
- Sem links superiores duplicados, sem botão de menu no celular e sem JavaScript obsoleto de abertura de menu.
- Árvore central original com os **17 círculos** e mapeamento existente preservados.
- Navegação alternativa: seis destinos acessíveis na área da árvore e links curtos no rodapé.
- Título/tooltip acessíveis ao teclado e hover com mecanismo de Escape preservado.
- No celular, o botão do cabeçalho abreviado é anunciado por leitores de tela com nome completo.
- AcessaData IDE e AcessaDataAI não são divulgados publicamente nesta versão; seus códigos de desenvolvimento não são alterados. AcessaData-Health conserva as ressalvas existentes.
- **Executar:** `python build.py`, `python -m unittest test_site -v` e `python -m http.server 8000 --bind 127.0.0.1 --directory dist`.
- Esta é uma revisão de usabilidade e design, não uma certificação WCAG 2.2 AA.

## Segurança (v4.8)

Veja `AUDITORIA_SEGURANCA_v4_8.md`. O build copia `_headers` para `dist/_headers` e o arquivo é interpretado somente na Cloudflare Pages.

## Publicação simplificada — arquitetura homologada em 2026-11-23

Esta seção descreve o pacote estático homologado para o site institucional da AcessaData-ONE.
O endereço legado citado acima é histórico; não corresponde a uma quarta página publicada.

### Navegação pública

- **Homepage:** `/index.html` (rota canônica `/`), com a seção Agricultura de Precisão e os serviços apresentados no site.
- **Storytelling interativo:** `/storytelling/`, acessado pelo botão **Explorar estudo de caso** da homepage.
- **Relatório Quarto:** `/relatorios/acessadata-health-quarto.html`, acessado pelo cartão **Quarto v2 · 2024** no Storytelling. O Cloudflare Pages pode normalizar a URL para a forma sem `.html`.
- A distribuição contém **exatamente três páginas HTML**. Não há páginas independentes de portfólio interativo ou projeto Health.
- Cinco redirecionamentos históricos HTTP 301 estão declarados no arquivo `_redirects` e foram verificados na prévia.

### Fonte, geração e verificações

- `build.py` e `content/site.json` geram a homepage e configuram o link para `/storytelling/`.
- `publicacao_extras/` contém 35 recursos complementares de publicação: Storytelling, Quarto, seus dados e dependências, além de `_redirects`.
- `manifesto_extras.json`, `site_ap_09_checks.py` e `test_site_simplificado.py` fazem parte dos controles versionáveis.
- Para gerar novamente, execute `python -B build.py` **com `dist/` ausente ou vazio**. O gerador recusa uma pasta `dist/` não vazia para evitar mistura de versões.
- A suíte executada com `python -B -m unittest discover -s . -p "test_*.py" -v` passou em **93/93 testes** na SITE-AP-11-C.
- A distribuição local reproduziu **49/49 arquivos por SHA-256** em relação ao pacote SITE-AP-08-H; a prévia Cloudflare confirmou **47/47 recursos HTTPS** e **5/5 redirecionamentos**.
- Os arquivos `_headers` e `_redirects` são consumidos pelo Cloudflare Pages e não são servidos como recursos estáticos convencionais.

### Alcance científico e implantação

- O relatório Health apresenta contagens agregadas e ressalvas metodológicas; não demonstra causalidade, nem substitui auditoria independente do microdado original do SIM.
- A checagem determinística `validate_health()` permanece na fonte e verifica consistência interna dos dados agregados.
- A implantação homologada em `bf5fd2d5.acessadata-one.pages.dev` é **Preview**, não Production.
- O projeto Cloudflare Pages utiliza **Direct Upload**. Versionar a fonte em Git não publica automaticamente no domínio de produção.
- Publicação em Production exige uma decisão e um procedimento próprios, com nova conferência de integridade.
