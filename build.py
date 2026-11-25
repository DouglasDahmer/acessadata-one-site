"""Gera o site estático da AcessaData-ONE. Python >=3.10, sem dependências extras.
Execute: python build.py
Prévia local: python -m http.server 8000 --directory dist
"""
from __future__ import annotations
from pathlib import Path
from html import escape
import json
import re
import shutil
import csv

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'

ICONS = {
    'analytics': '<path d="M3 3v18h18"/><path d="M7 16l4-5 4 3 5-7"/>',
    'pipeline': '<rect x="2" y="4" width="7" height="6" rx="1"/><rect x="15" y="4" width="7" height="6" rx="1"/><rect x="8.5" y="16" width="7" height="6" rx="1"/><path d="M5.5 10v4h6.5v2M18.5 10v4H12"/>',
    'quality': '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z"/><path d="m9 12 2 2 4-4"/>',
    'database': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    'chart': '<path d="M3 3v18h18M7 15v3M12 10v8M17 6v12"/>',
    'layers':'<path d="m12 2-9 5 9 5 9-5-9-5ZM3 12l9 5 9-5M3 17l9 5 9-5"/>',
    'menu':'<path d="M4 7h16M4 12h16M4 17h16"/>',
    'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2A19.79 19.79 0 0 1 11.19 18a19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.11-8.62A2 2 0 0 1 4.07 1.2h3a2 2 0 0 1 2 1.72c.12.96.35 1.91.67 2.81a2 2 0 0 1-.45 2.11L7.4 9.73a16 16 0 0 0 6.87 6.87l1.89-1.89a2 2 0 0 1 2.11-.45c.9.32 1.85.55 2.81.67A2 2 0 0 1 22 16.92Z"/>'
}

def icon(name: str) -> str:
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'

def e(s: object) -> str:
    return escape(str(s), quote=True)

def service_cards(data: list[dict]) -> str:
    cards=[]
    for s in data:
        items=''.join(f'<li>{e(v)}</li>' for v in s['items'])
        problem = e(s['client_problem'])
        delivery = e(s['delivery'])
        cards.append(f'''<article id="{e(s["anchor"])}" class="service-card">
        <div class="service-top"><span class="service-icon">{icon(s['icon'])}</span><span class="service-index">{e(s['number'])} / 03</span></div>
        <div class="service-tag">{e(s['tag'])}</div><h3>{e(s['name'])}</h3>
        <p class="service-intro">{e(s['description'])}</p>
        <div class="service-outcome"><p><strong>Desafio que ajudamos a resolver</strong>{problem}</p><p><strong>Entrega prevista</strong>{delivery}</p></div>
        <div class="service-capabilities"><span class="service-capabilities-title">O que envolve</span><ul>{items}</ul></div>
        </article>''')
    return '\n'.join(cards)

def project_cards(projects: list[dict]) -> str:
    out=[]
    for p in projects:
        tags=''.join(f'<span>{e(x)}</span>' for x in p['tags'])
        url = p.get('case_study_url')
        if url and (p.get('anchor') != 'acessadata-health' or url != '/storytelling/'):
            raise ValueError('Link de estudo de caso externo ou inválido.')
        detail_link = (f'<a class="project-case-link" href="{e(url)}">Explorar estudo de caso <span aria-hidden="true">↗</span></a>' if url else '')
        out.append(f'''<article id="{e(p["anchor"])}" class="project-card">
        <div class="project-art {e(p['style'])}" aria-hidden="true"><div class="art-core"><div class="art-mark">✳</div><div class="art-big">{e(p['figure'])}</div><div class="art-caption">{e(p['figure_note'])}</div></div></div>
        <div class="project-content"><div class="project-kind">{e(p['kind'])}</div><h3>{e(p['name'])}</h3><p>{e(p['lead'])}</p><div class="project-tags">{tags}</div><div class="project-status">{e(p['state'])}</div>{detail_link}</div>
        </article>''')
    return '\n'.join(out)


# Positions are design tokens, never taken directly from external JSON.
TREE_SLOTS = ('servicos', 'projetos', 'futuro', 'metodo', 'sobre', 'contato')

def tree_navigation(branches: list[dict]) -> str:
    if len(branches) != len(TREE_SLOTS) or {b.get('target') for b in branches} != set(TREE_SLOTS):
        raise ValueError('A arvore deve conter exatamente os seis destinos oficiais do site.')
    nodes = []
    for b in branches:
        key=b['target']
        phase = '<span class="leaf-phase">Planejado</span>' if key == 'futuro' else ''
        nodes.append(
            f'<li class="tree-leaf tree-leaf--{key}">'
            f'<a class="tree-leaf-link" href="#{key}" aria-label="{e(b["name"])} — {e(b["summary"])}">'
            f'<span class="leaf-knot" aria-hidden="true"></span>'
            f'<span class="leaf-copy"><strong>{e(b["name"])}</strong>'
            f'<small>{e(b["summary"])}</small>{phase}</span>'
            f'<span class="leaf-arrow" aria-hidden="true">↗</span>'
            '</a></li>'
        )
    return '\n'.join(nodes)


MAP_PATH = ROOT / 'content' / 'mapa_circulos.json'
EXPECTED_TREE_IDS = set(range(1, 18))
TREE_MAIN_IDS = {1, 3, 4, 5, 7, 12}

def tree_original_navigation() -> tuple[str, str]:
    """Create accessible links and an explicit mobile/keyboard alternative.

    Markers come from coordinates recorded against the ORIGINAL user-supplied tree;
    the artwork itself is never redrawn or edited to add labels.
    """
    payload = json.loads(MAP_PATH.read_text(encoding='utf-8'))
    points = payload['pontos']
    ids = [item['id'] for item in points]
    if set(ids) != EXPECTED_TREE_IDS or len(ids) != 17:
        raise ValueError('O mapa da árvore precisa conter 17 círculos distintos.')
    hrefs = set()
    dots = []
    groups = {'principal': [], 'secundario': []}
    for p in points:
        title = str(p['titulo'])
        summary = str(p['descricao'])
        href = str(p['destino_planejado'])
        group = str(p['classe'])
        x, y = float(p['x_percent']), float(p['y_percent'])
        if (not href.startswith('#') or href in hrefs or group not in groups
                or (p['id'] in TREE_MAIN_IDS) != (group == 'principal')
                or not 0 < x < 100 or not 0 < y < 100):
            raise ValueError(f'Círculo incorreto ou destino duplicado: {p!r}')
        hrefs.add(href)
        place = 'dot-below' if y < 24 else 'dot-above'
        # aria-label gives an unambiguous accessible name even when tooltip is hidden.
        dots.append(
            f'<a class="tree-dot {place} tree-dot--{group}" '
            f'style="left:{x:.3f}%;top:{y:.3f}%" '
            f'href="{e(href)}" aria-label="{e(title)} — {e(summary)}" '
            f'data-tree-label="{e(title)}" data-tree-description="{e(summary)}">'
            '<span class="tree-dot-halo" aria-hidden="true"></span>'
            '<span class="tree-dot-tooltip" aria-hidden="true">'
            f'<strong>{e(title)}</strong><small>{e(summary)}</small>'
            '<span class="tree-dot-action">Abrir seção ↗</span></span></a>'
        )
        groups[group].append(
            '<li><a href="' + e(href) + '"><span class="node-list-mark" aria-hidden="true"></span>'
            + '<span><strong>' + e(title) + '</strong><small>' + e(summary) + '</small></span>'
            + '<span class="node-list-arrow" aria-hidden="true">↗</span></a></li>'
        )
    sidebar = ('<div class="tree-mobile-links">'
               '<h3>Áreas principais</h3><ul class="tree-node-list tree-node-list--main">'
               + ''.join(groups['principal']) + '</ul>'
               '<details class="tree-extra-details">'
               '<summary>Explorar mais 11 caminhos <span aria-hidden="true">＋</span></summary>'
               '<p>Serviços especializados, projetos e princípios de atuação.</p>'
               '<ul class="tree-node-list tree-node-list--other">'
               + ''.join(groups['secundario']) + '</ul></details></div>')
    return '\n'.join(dots), sidebar

def step_cards(data: list[dict]) -> str:
    return '\n'.join(f'<article class="step"><span class="step-num">{e(x["n"])} / 04</span><h3>{e(x["title"])}</h3><p>{e(x["desc"])}</p></article>' for x in data)

def whatsapp_url(phone: object) -> str:
    digits = str(phone)
    if not (digits.isascii() and digits.isdecimal() and digits.startswith('55')
            and 12 <= len(digits) <= 13):
        raise ValueError('Telefone do WhatsApp inválido: utilize DDI e DDD, apenas números.')
    return 'https://wa.me/' + digits

TEMPLATE=r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#f7fafb">
<title>__TITLE__</title>
<meta name="description" content="__DESCRIPTION__">
<meta name="robots" content="index,follow">
<meta property="og:type" content="website">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESCRIPTION__">
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="preload" href="assets/acessadataone-horizontal.webp" as="image" type="image/webp">
<!-- Tipografia de destaque; se a rede estiver indisponível, usa fontes locais. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Michroma&amp;display=swap">
<link rel="stylesheet" href="assets/style.css">
<script src="assets/main.js" defer></script>
</head>
<body>
<a class="skip-link" href="#conteudo">Ir para o conteúdo principal</a>
<header class="site-header minimal-site-header">
 <div class="wrap header-inner header-inner--minimal">
  <a href="#inicio" class="logo-link" aria-label="AcessaData-ONE — voltar ao início"><img src="assets/acessadataone-horizontal.webp" alt="AcessaData-ONE" width="1300" height="418"></a>
  <a href="#contato" class="btn btn-primary header-contact" aria-label="Entrar em contato com a AcessaData-ONE"><span class="header-contact-long">Entrar em contato</span><span class="header-contact-short" aria-hidden="true">Contato</span><span class="inline-arrow" aria-hidden="true">↗</span></a>
 </div>
</header>
<main id="conteudo">
<section class="hero tree-central-hero" id="inicio" aria-labelledby="hero-title">
 <div class="wrap">
  <div class="tree-central-heading">
   <span class="pill"><span class="pill-dot" aria-hidden="true"></span><span class="brand-signature">Data · Innovation · Technology</span></span>
   <h1 id="hero-title">Transformamos dados em <em>possibilidades.</em></h1>
   <p class="tree-central-intro">Análise de Dados, pipelines analíticos e qualidade da informação para transformar processos complexos em decisões mais claras.</p>
   <p class="tree-explore-note" id="tree-help">Explore os círculos da árvore para navegar pelo site. No celular, escolha uma área logo abaixo.</p>
  </div>
  <nav class="original-tree-nav" aria-label="Árvore de navegação da AcessaData-ONE" aria-describedby="tree-help">
   <div class="original-tree-frame">
    <img class="original-tree-art" src="assets/arvore-original.webp" width="1770" height="1415" alt="" fetchpriority="high">
    <div class="original-tree-dots" aria-label="Círculos navegáveis da árvore">
     __TREE_DOTS__
    </div>
   </div>
   <p class="tree-instruction">Passe o mouse sobre um círculo ou navegue com <kbd>Tab</kbd>; pressione <kbd>Enter</kbd> para abrir. <kbd>Esc</kbd> oculta a descrição.</p>
   __TREE_MOBILE_LIST__
  </nav>
  <p class="tree-central-footer">Empresa Simples de Inovação (Inova Simples) · RS, Brasil</p>
 </div>
</section>
<section id="ecossistema" class="section ecosystem-roots" aria-labelledby="ecosystem-title"><div class="wrap">
 <div class="section-head"><span class="eyebrow">NOSSAS RAÍZES</span><h2 id="ecosystem-title">Uma base sólida para cada novo galho.</h2><p>Nossa identidade une dados, tecnologia e inovação. Estes princípios orientam todas as áreas que crescem a partir da AcessaData-ONE.</p></div>
 <div class="roots-grid">
  <article id="usabilidade"><span class="root-icon" aria-hidden="true">01</span><h3>Engenharia de Usabilidade</h3><p>Fluxos claros, linguagem compreensível, prevenção de erros e experiência orientada às necessidades reais das pessoas.</p></article>
  <article id="acessibilidade"><span class="root-icon" aria-hidden="true">02</span><h3>Acessibilidade</h3><p>Teclado, tecnologias assistivas e design responsivo desde o planejamento, com testes e melhoria contínua.</p></article>
  <article><span class="root-icon" aria-hidden="true">03</span><h3>Rigor e rastreabilidade</h3><p>Dados verificáveis, testes reproduzíveis, documentação transparente e comunicação responsável de resultados.</p></article>
 </div>
 </div></section>
<section id="da-semente-aos-frutos" class="section brand-story" aria-labelledby="brand-story-title">
<div class="wrap brand-story-grid">
  <div class="brand-story-copy">
    <span class="eyebrow">IDENTIDADE ACESSADATA-ONE</span>
    <h2 id="brand-story-title">Da semente, aos frutos.</h2>
    <p>Assim como uma semente encontra na terra as condições para crescer e dar frutos, os dados, quando explorados com método e propósito, podem revelar conhecimentos, impulsionar descobertas e gerar resultados que fazem a diferença.</p>
    <p class="brand-story-motto" lang="en">Nurturing Insights. Harvesting Growth.</p>
  </div>
  <figure class="brand-story-media">
    <video controls preload="none" playsinline width="1280" height="720"
      poster="assets/acessadata-arvore-poster.webp"
      aria-label="Vídeo institucional: da semente ao crescimento da árvore AcessaData-ONE"
      aria-describedby="brand-story-video-description">
      <source src="assets/acessadata-arvore-institucional-web.mp4" type="video/mp4">
      Seu navegador não suporta vídeo HTML5.
    </video>
    <figcaption id="brand-story-video-description">Animação silenciosa de aproximadamente dez segundos.</figcaption>
  </figure>
</div>
</section>
<section id="servicos" class="section" aria-labelledby="services-title"><div class="wrap">
 <div class="section-head"><span class="eyebrow">O QUE FAZEMOS</span><h2 id="services-title">Soluções de dados para problemas reais.</h2><p>Começamos pelo problema do seu negócio e definimos entregas claras: análises, fluxos automatizados e verificações de qualidade.</p></div>
 <div class="service-grid">__SERVICES__</div>
 <aside id="consultoria" class="small-spotlight"><h3>Consultoria tecnológica</h3><p>Diagnóstico de processos e orientação para organizar soluções em Dados e tecnologia, com escopo definido conforme a necessidade do projeto.</p></aside>
</div></section>
<!-- SITE-AP-02: agricultura de precisao -->
<section id="agricultura-precisao" class="section ap-focus ap-showcase" aria-labelledby="ap-title">
  <div class="ap-showcase__container">
    <div class="ap-showcase__intro">
      <p class="ap-showcase__eyebrow">AGRICULTURA DE PRECISÃO · SOLUÇÕES EM DADOS ESPACIAIS</p>
      <h2 id="ap-title">Dados confiáveis para decisões mais precisas no campo.</h2>
      <p class="ap-showcase__lead">Da organização de bases geográficas à auditoria de mapas, apoiamos consultorias agronômicas, agtechs e operações agrícolas com diagnósticos técnicos, evidências e entregáveis verificáveis.</p>
      <p class="ap-showcase__contact-note">Para solicitar um diagnóstico, utilize os canais disponíveis na seção Contato.</p>
    </div>

    <div class="ap-showcase__available" aria-labelledby="ap-services-title">
      <div class="ap-showcase__section-heading">
        <div>
          <p class="ap-showcase__kicker">01 · SERVIÇOS CONTRATÁVEIS</p>
          <h3 id="ap-services-title">Serviços disponíveis agora</h3>
          <p>Engenharia e qualidade de dados, com escopo, critérios de aceitação e entregáveis definidos para cada projeto.</p>
        </div>
        <span class="ap-showcase__availability">Diagnóstico · Saneamento · Auditoria</span>
      </div>
      <div class="ap-showcase__service-grid">
        <article class="ap-showcase__service">
          <span class="ap-showcase__number" aria-hidden="true">01</span>
          <h4>Diagnóstico de Dados Espaciais</h4>
          <p>Avaliamos cobertura, completude, consistência, origem, formatos e sistemas de referência das bases disponíveis.</p>
          <p class="ap-showcase__deliverable"><strong>Entrega:</strong> parecer técnico com riscos e prioridades de tratamento.</p>
        </article>
        <article class="ap-showcase__service">
          <span class="ap-showcase__number" aria-hidden="true">02</span>
          <h4>Limpeza e Padronização de Bases</h4>
          <p>Tratamos atributos, formatos, duplicidades e referências espaciais, utilizando R, QGIS e Python conforme o problema.</p>
          <p class="ap-showcase__deliverable"><strong>Entrega:</strong> base tratada e registro das transformações executadas.</p>
        </article>
        <article class="ap-showcase__service">
          <span class="ap-showcase__number" aria-hidden="true">03</span>
          <h4>Auditoria de Geometrias e Coordenadas</h4>
          <p>Investigamos geometrias inválidas, sobreposições e inconsistências de datum, projeção e zona UTM.</p>
          <p class="ap-showcase__deliverable"><strong>Entrega:</strong> relatório de inconsistências e evidências para correção.</p>
        </article>
      </div>
      <div class="ap-showcase__field-problem">
        <span class="ap-showcase__field-symbol" aria-hidden="true">⌖</span>
        <div>
          <strong>O impacto no campo</strong>
          <p>Erros de referência espacial — como configurações inconsistentes de SIRGAS 2000 e zonas UTM —, polígonos sobrepostos e limites desalinhados podem comprometer mapas, estimativas de área e a preparação de arquivos para monitores de máquinas. Nossa auditoria ajuda a identificar essas falhas antes do uso operacional; a compatibilidade de exportação depende do equipamento e do formato exigido.</p>
        </div>
      </div>
    </div>

    <div id="laboratorio-pd" class="ap-showcase__lab" aria-labelledby="ap-research-title">
      <div class="ap-showcase__lab-heading">
        <div>
          <p class="ap-showcase__kicker">02 · PESQUISA APLICADA</p>
          <h3 id="ap-research-title">Laboratório &amp; P&amp;D</h3>
          <p>Linhas de desenvolvimento que ampliam a visão tecnológica da AcessaData-ONE, separadas dos serviços disponíveis.</p>
        </div>
        <span class="ap-showcase__lab-tag">Pesquisa e prototipação</span>
      </div>
      <div class="ap-showcase__lab-grid">
        <article class="ap-showcase__lab-card">
          <span class="ap-showcase__lab-label">RUST · ENGENHARIA DE SOFTWARE</span>
          <h4>Motor de processamento e validação</h4>
          <p>Pesquisa de componentes locais em Rust para verificações determinísticas, rastreabilidade e processamento geoespacial eficiente.</p>
        </article>
        <article class="ap-showcase__lab-card">
          <span class="ap-showcase__lab-label">IA EMBARCADA · SISTEMAS DE BORDA</span>
          <h4>Redes neurais e sensoriamento</h4>
          <p>Estudos de arquiteturas para integrar sensores e inferência local em microcontroladores e dispositivos de borda voltados ao ambiente agrícola.</p>
        </article>
      </div>
    </div>

    <p class="ap-showcase__positioning"><strong>Nosso compromisso:</strong> atuamos hoje na engenharia, no saneamento e na auditoria de dados espaciais, com métodos documentados e resultados rastreáveis; as iniciativas em Rust e IA embarcada integram o laboratório de P&amp;D e são avaliadas separadamente.</p>
  </div>
</section>
<!-- /SITE-AP-02 -->
<section id="projetos" class="section projects" aria-labelledby="projects-title"><div class="wrap">
 <div class="section-head"><span class="eyebrow eyebrow-light">PORTFÓLIO EM EVOLUÇÃO</span><h2 id="projects-title">Pesquisa aplicada e estudos técnicos.</h2><p>Estudos técnicos em evolução, com métodos, resultados e limitações documentados.</p></div>
 <div class="project-grid">__PROJECTS__</div>
 <p class="projects-after">Os projetos apresentados são trabalhos próprios em diferentes estágios de desenvolvimento. Não representam produtos comerciais já lançados nem contratos executados para clientes.</p>
</div></section>
<section id="metodo" class="section process" aria-labelledby="method-title"><div class="wrap">
 <div class="section-head"><span class="eyebrow">COMO TRABALHAMOS</span><h2 id="method-title">Da pergunta certa ao resultado confiável.</h2><p>Mais do que gerar gráficos, buscamos construir soluções verificáveis e fáceis de manter.</p></div>
 <div class="steps">__STEPS__</div>
 <aside id="estudos" class="small-spotlight"><h3>Estudos e evidências</h3><p>Documentação, hipóteses, limitações e testes reproduzíveis orientam nossos projetos técnicos e estudos de caso.</p></aside>
</div></section>
<section id="pesquisa" class="section future" aria-labelledby="future-title"><div class="wrap future-grid">
 <div id="visao-futuro" class="future-art" aria-hidden="true"><div class="dna-lines"><span></span><span></span><span></span><span></span><span></span><span></span><span></span></div><span class="future-art-caption">DADOS • CIÊNCIA • VIDA</span></div>
 <div id="bioinformatica" class="future-copy"><span class="eyebrow">GALHO EM DESENVOLVIMENTO · VISÃO DE FUTURO</span><h2 id="future-title">Bioinformática: um novo horizonte de pesquisa.</h2><p>Nossa perspectiva de longo prazo é integrar métodos de Ciência de Dados à pesquisa em Bioinformática, explorando aplicações computacionais em ciências da vida.</p><p>A <strong>AcessaData-Health</strong> é hoje um projeto de análise epidemiológica de dados públicos. Ele não é apresentado como pesquisa genômica nem como serviço de Bioinformática já disponível.</p><div class="future-chip">Expansão planejada · sem oferta comercial nesta fase</div></div>
</div></section>
<section id="sobre" class="section about" aria-labelledby="about-title"><div class="wrap about-grid">
 <div><span class="eyebrow">SOBRE O PROJETO</span><h2 id="about-title">Tecnologia acessível. Dados com responsabilidade.</h2><p>A AcessaData-ONE é uma Empresa Simples de Inovação (Inova Simples), voltada à Análise de Dados, desenvolvimento de software e soluções analíticas. A proposta é combinar ferramentas modernas com processos transparentes de validação e documentação.</p><p>Este portfólio reúne projetos e estudos em Ciência e Análise de Dados, desenvolvidos com foco no aprendizado contínuo, na aplicação prática do conhecimento e na busca por resultados confiáveis.</p><div class="about-checks"><span>Experiência prática de desenvolvimento e análise de dados</span><span>Rigor técnico, limites explícitos e testes reproduzíveis</span><span>Usabilidade e acessibilidade como princípios de projeto</span></div></div>
 <aside class="founder-card" aria-label="Apresentação e contato de Douglas H.S. Dahmer">
  <div class="founder-layout">
   <div class="founder-copy">
    <div class="founder-tag">DESENVOLVIMENTO E DIREÇÃO TÉCNICA</div>
    <h3>__FOUNDER__</h3>
    <p>Estudante de Ciência de Dados, desenvolvedor dos projetos e responsável pela estruturação da AcessaData-ONE.</p>
    <div class="founder-whatsapp" aria-label="Telefone profissional: __PHONE_DISPLAY__">
     <span class="founder-whatsapp-icon" aria-hidden="true">__PHONEICON__</span>
     <span><small>Contato profissional</small><strong>__PHONE_DISPLAY__</strong></span>
    </div>
   </div>
   <figure class="founder-portrait">
    <img src="assets/douglas-hs-dahmer-perfil.webp" alt="Retrato de Douglas H.S. Dahmer" width="960" height="960" loading="lazy" decoding="async">
   </figure>
  </div>
  <div class="founder-bottom"><span>Ciência de Dados · Engenharia Analítica</span><strong>RS, Brasil</strong></div>
 </aside>
</div></section>
<section id="contato" class="contact" aria-labelledby="contact-title"><div class="wrap contact-grid">
 <div><span class="eyebrow eyebrow-light">VAMOS CONVERSAR?</span><h2 id="contact-title">Seu próximo projeto pode começar com uma boa pergunta.</h2><p>Conte qual é o desafio, quais dados estão disponíveis e que resultado você pretende alcançar. Respondemos para avaliar o escopo e os próximos passos.</p></div>
 <div class="contact-actions">
 <p class="contact-data-note">Por segurança, não envie dados pessoais sensíveis, senhas ou bases confidenciais no primeiro contato.</p>
 <a href="__WHATSAPP_URL__" class="btn btn-whatsapp" aria-label="Abrir conversa pelo WhatsApp com a AcessaData-ONE no número __PHONE_DISPLAY__">__PHONEICON__ Falar pelo WhatsApp <span class="inline-arrow" aria-hidden="true">↗</span></a>
 <a href="mailto:__EMAIL__?subject=Contato%20-%20AcessaData-ONE" class="btn btn-light">Enviar e-mail <span class="inline-arrow" aria-hidden="true">↗</span></a>
 </div>
</div></section>
</main>
<footer class="site-footer"><div class="wrap footer-inner footer-inner--minimal"><span><strong>AcessaData-ONE</strong> · &copy; <span data-year>2026</span> · ACESSADATA-ONE INOVA SIMPLES (I.S.) · CNPJ: __CNPJ__</span><a class="footer-top" href="#inicio">Voltar ao topo ↑</a></div></footer>
</body></html>'''


HEALTH_FILE=ROOT/'content'/'estudo_health_rs_2024.json'
HEALTH_OUTPUT='estudo-acessadata-health-rs-2024.html'

def thousands(n: int) -> str:
    return format(n, ',').replace(',', '.')

def validate_health(data: dict) -> None:
    total=int(data['cancer_deaths_rs'])
    if total <= 0 or sum(int(x['deaths']) for x in data['sex']) != total:
        raise ValueError('Inconsistência nos totais por sexo.')
    if sum(int(x['deaths']) for x in data['ages']) != total:
        raise ValueError('Inconsistência nos totais por faixa etária.')
    if len(data['top_codes']) != 10 or len({x['code'] for x in data['top_codes']}) != 10:
        raise ValueError('Lista CID-10 inválida.')
    if not all(re.fullmatch(r'C[0-9]{2}',x['code']) and int(x['deaths'])>=0 for x in data['top_codes']):
        raise ValueError('Dados CID-10 inválidos.')
    if sum(x['deaths'] for x in data['top_codes']) > total:
        raise ValueError('Subtotais CID-10 maiores que o conjunto.')

def health_chart(items: list[dict], label_key: str, max_value: int | None=None) -> str:
    top=max_value or max(item['deaths'] for item in items)
    rows=[]
    for item in items:
        label=str(item[label_key])
        n=int(item['deaths'])
        width=f'{n/top*100:.2f}%'
        rows.append('<div class="health-bar-row"><span class="health-bar-name">'+e(label)+'</span>'
                    + '<span class="health-bar-track"><span class="health-bar-fill" style="width:'+width+'"></span></span>'
                    +'<strong>'+thousands(n)+'</strong></div>')
    return '<div class="health-bar-chart" aria-hidden="true">'+''.join(rows)+'</div>'

def health_table(items: list[dict], key: str, col_title: str, caption: str) -> str:
    rows=''.join('<tr><th scope="row">'+e(item[key])+'</th><td>'+thousands(item['deaths'])+'</td></tr>' for item in items)
    return ('<div class="health-table-wrap"><table class="health-data-table"><caption>'+e(caption)+'</caption>'
            +'<thead><tr><th scope="col">'+e(col_title)+'</th><th scope="col">Óbitos (contagem)</th></tr></thead>'
            +'<tbody>'+rows+'</tbody></table></div>')

def render_health_study(d: dict) -> str:
    validate_health(d)
    total=int(d['cancer_deaths_rs'])
    male=next(x['deaths'] for x in d['sex'] if x['label']=='Masculino')
    female=next(x['deaths'] for x in d['sex'] if x['label']=='Feminino')
    assert male+female==total
    sex_chart=health_chart(d['sex'],'label',max_value=max(male,female))
    age_chart=health_chart(d['ages'],'label')
    top_chart=health_chart(d['top_codes'],'code')
    step_list=''.join('<li>'+e(step)+'</li>' for step in d['pipeline'])
    controls=''.join('<li>'+e(step)+'</li>' for step in d['checks'])
    caveats=''.join('<li>'+e(step)+'</li>' for step in d['limitations'])
    return f'''<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><meta name="theme-color" content="#f7fafb">
<title>{e(d['title'])} | AcessaData-ONE</title>
<meta name="description" content="Estudo de caso técnico com resultados agregados do SIM 2024: óbitos por câncer no Rio Grande do Sul, metodologia e limitações.">
<link rel="icon" href="assets/favicon.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Michroma&amp;display=swap">
<link rel="stylesheet" href="assets/style.css">
</head><body class="health-study-body">
<a class="skip-link" href="#conteudo">Ir diretamente ao conteúdo</a>
<header class="site-header"><div class="wrap header-inner health-header">
<a class="logo-link" href="index.html#inicio" aria-label="AcessaData-ONE — página inicial"><img src="assets/acessadataone-horizontal.webp" width="1300" height="418" alt="AcessaData-ONE"></a>
<nav class="health-header-nav" aria-label="Navegação do estudo"><a href="index.html#projetos">← Portfólio</a><a href="#resultados">Resultados</a><a href="#metodologia">Método</a><a href="#limites">Limitações</a></nav>
</div></header>
<main id="conteudo">
<section class="health-hero"><div class="wrap health-hero-grid">
<div><span class="eyebrow">ESTUDO DE CASO · PESQUISA APLICADA</span>
<h1>Mortalidade por câncer no <em>Rio Grande do Sul</em></h1>
<p class="health-subtitle">Registros do SIM 2024 · análise exploratória e pipeline em Python e SQL</p>
<p class="health-status">{e(d['study_status'])}</p>
<div class="health-hero-actions"><a class="btn btn-primary" href="#resultados">Explorar indicadores ↘</a><a class="btn btn-ghost" href="#metodologia">Entender a metodologia</a></div>
</div>
<aside class="health-hero-number" aria-label="Total agregado no estudo"><span>RESULTADO DO PROCESSAMENTO ANTERIOR</span><strong>{thousands(total)}</strong><p>óbitos classificados como câncer na seleção de residentes do RS em 2024</p><small>Contagem bruta · não é taxa padronizada</small></aside>
</div></section>
<section class="health-summary wrap" aria-label="Síntese dos indicadores">
<div class="health-metric"><span>Registros nacionais processados</span><strong>{thousands(d['processed_national'])}</strong><small>Arquivo de referência SIM 2024</small></div>
<div class="health-metric"><span>Registros de residentes do RS</span><strong>{thousands(d['processed_rs'])}</strong><small>Antes do filtro de câncer</small></div>
<div class="health-metric"><span>Masculino</span><strong>{thousands(male)}</strong><small>{f'{male/total*100:.2f}'.replace('.',',')}% dos óbitos selecionados</small></div>
<div class="health-metric"><span>Feminino</span><strong>{thousands(female)}</strong><small>{f'{female/total*100:.2f}'.replace('.',',')}% dos óbitos selecionados</small></div>
</section>
<section id="resultados" class="health-results section"><div class="wrap">
<div class="section-head"><span class="eyebrow">RESULTADOS AGREGADOS</span><h2>O que os registros mostram?</h2><p>Indicadores derivados do processamento relatado no projeto. Cada gráfico possui uma tabela textual equivalente.</p></div>
<div class="health-results-grid">
<article class="health-figure-card"><h3>Distribuição por sexo</h3><p>Participação nas contagens de óbitos selecionados.</p>{sex_chart}{health_table(d['sex'],'label','Sexo','Óbitos por sexo, RS, SIM 2024')}</article>
<article class="health-figure-card"><h3>Distribuição por faixa etária</h3><p>Estratificação etária sem padronização populacional.</p>{age_chart}{health_table(d['ages'],'label','Idade (anos)','Óbitos por faixa etária, RS, SIM 2024')}</article>
<article class="health-figure-card health-figure-wide"><h3>Dez códigos CID-10 mais frequentes na seleção</h3><p>Ranking por contagem bruta; valores não são taxas nem probabilidades individuais de adoecimento.</p>{top_chart}{health_table(d['top_codes'],'code','Código CID-10','Dez códigos mais frequentes, RS, SIM 2024')}</article>
</div></div></section>
<section id="metodologia" class="health-method section"><div class="wrap"><div class="section-head"><span class="eyebrow">PIPELINE REPRODUZÍVEL</span><h2>Do arquivo público ao indicador.</h2><p>Etapas técnicas documentadas no projeto AcessaData-Health.</p></div>
<ol class="health-steps">{step_list}</ol>
<div class="health-method-note"><h3>Controles já relatados</h3><ul>{controls}</ul><p>Essas verificações foram informadas no desenvolvimento do projeto. Não constituem, por si sós, uma auditoria independente da base original.</p></div>
</div></section>
<section id="limites" class="health-limit section"><div class="wrap health-limit-grid"><div>
<span class="eyebrow">TRANSPARÊNCIA METODOLÓGICA</span><h2>O que este estudo não demonstra.</h2><p>Contagens são úteis para descrever o conjunto analisado, mas precisam ser interpretadas dentro do escopo e das limitações da base.</p>
</div><div><ul class="health-caveat-list">{caveats}</ul></div></div></section>
<section class="health-source-section"><div class="wrap health-source-box"><div><span class="eyebrow">FONTE E PROVENIÊNCIA</span><h2>Dados públicos, métodos transparentes.</h2><p>Fonte de referência: <strong>{e(d['source_name'])}</strong>, Ministério da Saúde. Os resultados apresentados nesta página são agregados do projeto e não equivalem a uma tabulação oficial homologada.</p>
<p class="health-meta"><strong>Status do conjunto:</strong> {e(d['prepared_from'])}</p>
</div><div class="health-source-links"><a class="btn btn-primary" href="{e(d['source_url'])}" rel="noopener noreferrer" target="_blank">Consultar SIM 2024 ↗ <span class="sr-only">(abre nova aba)</span></a>
<a class="btn btn-ghost" href="dados/acessadata-health-rs-2024-resumo.json" download>Baixar agregados JSON ↓</a>
<a class="btn btn-ghost" href="dados/acessadata-health-rs-2024-top-cid.csv" download>Baixar ranking CSV ↓</a></div>
</div></section>
<section class="health-last-cta"><div class="wrap health-last-grid"><div><h2>Precisa organizar e validar seus dados?</h2><p>Conheça os serviços de Análise de Dados e pipelines analíticos da AcessaData-ONE.</p></div>
<a class="btn btn-light" href="index.html#contato">Entrar em contato ↗</a></div></section>
</main><footer><div class="wrap footer-inner"><span><strong>AcessaData-ONE</strong> · Estudo de caso técnico · 2026</span><span><a href="index.html#projetos">← Voltar ao portfólio</a></span></div></footer>
</body></html>'''

def write_health_outputs() -> None:
    d=json.loads(HEALTH_FILE.read_text('utf8'))
    validate_health(d)
    (OUT/'dados').mkdir(exist_ok=True)
    (OUT/'dados'/'acessadata-health-rs-2024-resumo.json').write_text(
        json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    with (OUT/'dados'/'acessadata-health-rs-2024-top-cid.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f)
        writer.writerow(['ano','uf_residencia','codigo_cid10','contagem_obitos','observacao'])
        for item in d['top_codes']:
            writer.writerow([d['period'],'RS',item['code'],item['deaths'],'Agregado da execução anterior; sujeito a revisão'])

def build() -> Path:
    d=json.loads((ROOT/'content'/'site.json').read_text(encoding='utf8'))
    phone = str(d['phone_e164'])
    whats = whatsapp_url(phone)
    replacements={
        '__TITLE__':e(d['title']), '__DESCRIPTION__':e(d['description']),
        '__SERVICES__':service_cards(d['services']), '__PROJECTS__':project_cards(d['projects']),
        '__TREE_DOTS__':tree_original_navigation()[0],
        '__TREE_MOBILE_LIST__':tree_original_navigation()[1],
        '__STEPS__':step_cards(d['steps']), '__FOUNDER__':e(d['founder']), '__CNPJ__':e(d['cnpj']), '__EMAIL__':e(d['email']),
        '__WHATSAPP_URL__':e(whats),
        '__PHONE_DISPLAY__':e(d['phone_display']),
        '__PHONE_E164__':e(phone), '__PHONEICON__':icon('phone'),
        '__MENUICON__':icon('menu'), '__DATABASEICON__':icon('database'),
        '__LAYERSICON__':icon('layers'), '__CHARTICON__':icon('chart')
    }
    html=TEMPLATE
    for source, value in replacements.items():
        html=html.replace(source,value)
    unreplaced = set(re.findall(r'__[A-Z][A-Z0-9_]*__', html))
    if unreplaced:
        raise ValueError(f'Variáveis do template não preenchidas: {sorted(unreplaced)}')
    if OUT.is_symlink() or (OUT.exists() and any(OUT.iterdir())):
        raise RuntimeError('DIST_DEVE_ESTAR_VAZIA')
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    # Cloudflare Pages aplica o arquivo _headers somente quando ele está na raiz do deploy.
    shutil.copyfile(ROOT/'_headers', OUT/'_headers')
    (OUT/'index.html').write_text(html,encoding='utf8')
    write_health_outputs()
    extras=ROOT/'publicacao_extras'
    if not extras.is_dir():
        raise FileNotFoundError('PUBLICACAO_EXTRAS_AUSENTE')
    shutil.copytree(extras,OUT,dirs_exist_ok=True)
    print(f'Pronto: {OUT / "index.html"}')
    print('Publicacao: homepage, storytelling e quarto')
    return OUT

if __name__=='__main__':
    build()
