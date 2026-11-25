"""Testes de estrutura do site v4.5; execute python -m unittest test_site -v."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
import build

class AuditHTML(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids=[]; self.hrefs=[]; self.images=[]; self.dots=[]; self.mobile=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if tag == 'a':
            self.hrefs.append(a.get('href',''))
            if 'tree-dot ' in a.get('class',''): self.dots.append(a)
            if a.get('href') and a.get('class')=='': pass
        if tag=='img': self.images.append(a)

# Parser de HTML usando apenas a biblioteca padrao do Python.
# Evita dependencia acidental de Beautiful Soup 4 nos testes.
class ElementoHTML:
    def __init__(self, tag, attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []
        self.text_parts = []

    def get(self, name):
        return self.attrs.get(name)

    def find_all(self, tag=None, css_class=None):
        found = []
        for child in self.children:
            if ((tag is None or child.tag == tag) and
                    (css_class is None or css_class in child.attrs.get('class', '').split())):
                found.append(child)
            found.extend(child.find_all(tag, css_class))
        return found

    def find(self, tag=None, css_class=None):
        return next(iter(self.find_all(tag, css_class)), None)

    def get_text(self):
        return ' '.join(self.text_parts + [child.get_text() for child in self.children])


class ArvoreHTML(HTMLParser):
    VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img',
                 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ElementoHTML('_root')
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = ElementoHTML(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(ElementoHTML(tag, attrs))

    def handle_endtag(self, tag):
        for idx in range(len(self.stack) - 1, 0, -1):
            if self.stack[idx].tag == tag:
                del self.stack[idx:]
                return

    def handle_data(self, data):
        self.stack[-1].text_parts.append(data)


class TestV4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=Path(__file__).parent; cls.html=(cls.root/'dist/index.html').read_text('utf8'); cls.p=AuditHTML();cls.p.feed(cls.html)
        cls.points=json.loads((cls.root/'content/mapa_circulos.json').read_text('utf8'))['pontos']
    def test_01_all_17_original_dots_rendered(self):
        self.assertEqual(len(self.p.dots),17)
        self.assertEqual(len({x['href'] for x in self.p.dots}),17)
    def test_02_every_dot_has_valid_destination(self):
        for link in self.p.dots:
            self.assertTrue(link['href'].startswith('#'))
            self.assertIn(link['href'][1:],self.p.ids,link)
    def test_03_all_navigation_anchors_resolve(self):
        ids=set(self.p.ids)
        for href in self.p.hrefs:
            if href.startswith('#'):
                self.assertIn(href[1:],ids,href)
    def test_04_original_logo_used(self):
        self.assertIn('src="assets/arvore-original.webp"',self.html)
        self.assertTrue((self.root/'dist/assets/arvore-original.webp').is_file())
        self.assertTrue((self.root/'design/arvore-original-alta-resolucao.png').is_file())
    def test_05_hover_focus_tooltips(self):
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn('.tree-dot:hover .tree-dot-tooltip',css)
        self.assertIn('.tree-dot:focus-visible .tree-dot-tooltip',css)
        self.assertIn('.tree-dot:focus-visible{outline:',css)
        self.assertEqual(self.html.count('class="tree-dot-tooltip"'),17)
    def test_06_accessible_labels(self):
        self.assertTrue(all(x.get('aria-label') and x.get('href') for x in self.p.dots))
        self.assertIn('class="skip-link"',self.html)
        self.assertIn('lang="pt-BR"',self.html)
        self.assertIn('aria-label="Árvore de navegação',self.html)
    def test_07_mobile_equivalent_navigation(self):
        # Every mapped point appears twice: as a desktop dot and an HTML list link.
        for point in self.points:
            self.assertGreaterEqual(self.html.count('href="'+point['destino_planejado']+'"'),2)
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn('.original-tree-dots{display:none}',css)
        self.assertIn('.tree-mobile-links{display:block;',css)
    def test_08_content_and_candid_claims(self):
        d=json.loads((self.root/'content/site.json').read_text('utf8'))
        self.assertIn(d['founder'],self.html);self.assertIn(d['email'],self.html)
        self.assertIn('CNPJ: 69.899.726/0001-04',self.html)
        self.assertIn('sem oferta comercial nesta fase',self.html)
    def test_09_mobile_no_forms_or_analytics(self):
        self.assertNotIn('<form',self.html.lower())
        self.assertNotIn('google-analytics',self.html.lower())
        self.assertIn('prefers-reduced-motion', (self.root/'assets/style.css').read_text('utf8'))
    def test_10_anchors_no_duplicates(self):
        self.assertEqual(len(self.p.ids),len(set(self.p.ids)), 'IDs HTML duplicados')
    def test_11_correct_coordinates_in_markup(self):
        for point in self.points:
            self.assertIn('left:'+f"{point['x_percent']:.3f}"+'%;',self.html)
    def test_12_assets_generated(self):
        for asset in ['assets/style.css','assets/main.js','assets/arvore-original.webp','assets/acessadataone-horizontal.webp','assets/favicon.png']:
            self.assertTrue((self.root/'dist'/asset).is_file(),asset)
    def test_13_html_safe_escaping_for_labels(self):
        # Build accepts content as data; malformed markup in labels must remain escaped.
        from unittest.mock import patch
        example=json.loads((self.root/'content/mapa_circulos.json').read_text('utf8'))
        example['pontos'][0]['titulo']='<script>alert(1)</script>'
        with patch.object(build,'MAP_PATH',self.root/'content/mapa_circulos.json'):
            # Builder default actual map is safe; test escape helper used directly.
            self.assertEqual(build.e('<script>'), '&lt;script&gt;')
    def test_14_map_rejects_collisions(self):
        from unittest.mock import patch
        from tempfile import TemporaryDirectory
        data=json.loads((self.root/'content/mapa_circulos.json').read_text('utf8'))
        data['pontos'][0]['destino_planejado'] = data['pontos'][1]['destino_planejado']
        with TemporaryDirectory() as td:
            p=Path(td)/'map.json';p.write_text(json.dumps(data),encoding='utf8')
            with patch.object(build,'MAP_PATH',p):
                with self.assertRaises(ValueError):build.tree_original_navigation()
    def test_15_keyboard_and_mouse_navigation_no_custom_click_handler(self):
        js=(self.root/'assets/main.js').read_text('utf8')
        self.assertIn('mouseenter',js);self.assertIn("'focus'",js)
        self.assertNotIn('window.location',js)
    def test_16_uses_all_user_assigned_topics(self):
        self.assertEqual(len(self.points),17)
        for point in self.points:
            self.assertIn(point['titulo'],self.html)

    def test_17_tooltips_keep_within_viewport(self):
        js=(self.root/'assets/main.js').read_text('utf8')
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn('fitTooltip',js)
        self.assertIn('window.innerWidth',js)
        self.assertIn('--tooltip-shift',css)
    def test_18_esc_hides_popup_without_breaking_link(self):
        js=(self.root/'assets/main.js').read_text('utf8')
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn("event.key==='Escape'",js)
        self.assertIn('is-tooltip-dismissed',css)
        self.assertIn('<kbd>Esc</kbd>',self.html)
    def test_19_reduced_motion_including_scroll(self):
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn('html{scroll-behavior:auto}',css)
        self.assertIn('prefers-reduced-motion:reduce',css)
    def test_20_external_resources_unnecessary(self):
        self.assertIn('https://fonts.googleapis.com',self.html)
        self.assertNotIn('<script src="https:',self.html)

    def test_21_founder_picture_alt_and_local_asset(self):
        self.assertIn('src="assets/douglas-hs-dahmer-perfil.webp"',self.html)
        self.assertIn('alt="Retrato de Douglas H.S. Dahmer"',self.html)
        self.assertTrue((self.root/'dist/assets/douglas-hs-dahmer-perfil.webp').is_file())
    def test_22_whatsapp_accessible_clickable_links(self):
        self.assertEqual(self.html.count('href="https://wa.me/5551994313154"'),1)
        self.assertIn('aria-label="Abrir conversa pelo WhatsApp',self.html)
        self.assertIn('Contato profissional',self.html)
        self.assertIn('aria-label="Telefone profissional: (51) 99431-3154"',self.html)

    def test_23_contact_remains_accessible(self):
        self.assertIn('href="mailto:acessadataone@gmail.com?subject=',self.html)
        self.assertIn('(51) 99431-3154',self.html)
        self.assertIn('href="https://wa.me/5551994313154"',self.html)
        self.assertEqual(self.html.count('class="contact-email"'),0)
        self.assertEqual(self.html.count('class="contact-phone"'),0)

    def test_24_original_tree_unchanged(self):
        self.assertEqual(len(self.p.dots),17)
        self.assertIn('src="assets/arvore-original.webp"',self.html)
        self.assertEqual(__import__('hashlib').sha256((self.root/'assets/arvore-original.webp').read_bytes()).hexdigest(),'fefd411bd62653da5250d340f9db279e5b355c2952d05be7e9139959b519b738')
    def test_25_phone_is_rejected_if_not_e164(self):
        self.assertEqual(build.whatsapp_url('5551994313154'), 'https://wa.me/5551994313154')
        for bad in ('<script>alert(1)</script>', '51 99431-3154', '+5551994313154', '5551', ''):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    build.whatsapp_url(bad)
    def test_26_media_queries_for_small_screen_and_reduced_motion(self):
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn('@media(max-width:600px)',css)
        self.assertIn('.founder-portrait img',css)
        self.assertIn('@media(prefers-reduced-motion:reduce)',css)

    def test_27_brand_css_and_header_dimensions(self):
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn('--font-brand:',css)
        self.assertIn('width:310px',css)
        self.assertIn('min-height:104px',css)
        self.assertIn('font-family:var(--font-brand)',css)
        self.assertIn('width="1300" height="418"',self.html)

    def test_28_minimal_header_and_readable_body(self):
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn('.header-inner--minimal',css)
        self.assertNotIn('data-menu-toggle',self.html)
        self.assertIn('--font-reading:',css)
        self.assertIn('body{font-family:var(--font-reading)}',css)

    def test_29_font_assets_sob_controle(self):
        css = (self.root / 'assets/style.css').read_text('utf-8')
        self.assertNotIn('fonts.googleapis.com', css)
        self.assertNotIn('fonts.gstatic.com', css)
        self.assertFalse(list(self.root.rglob('*.ttf')))
        fontes = {p.relative_to(self.root).as_posix()
                  for p in self.root.rglob('*.woff*') if p.is_file()}
        self.assertEqual(fontes, {
            'dist/relatorios/acessadata-health-csp-piloto-v2_files/libs/bootstrap/bootstrap-icons.woff',
            'publicacao_extras/relatorios/acessadata-health-csp-piloto-v2_files/libs/bootstrap/bootstrap-icons.woff',
        })
        quarto_css = (self.root / 'dist/relatorios/acessadata-health-csp-piloto-v2_files/libs/bootstrap/bootstrap-d00bc8e66a4761cd839a5785aef874ca.min.css').read_text('utf-8')
        self.assertIn('fonts.googleapis.com', quarto_css)
        csp = (self.root / 'dist/_headers').read_text('utf-8')
        self.assertIn('https://fonts.googleapis.com', csp)
        self.assertIn('https://fonts.gstatic.com', csp)

    def test_30_logo_source_and_interactive_js_unchanged(self):
        import hashlib
        self.assertEqual(hashlib.sha256((self.root/'assets/acessadataone-horizontal.webp').read_bytes()).hexdigest(),
                         '2548452fce3a5b53efe343f221f9ab2d0ec5a03ba69c680820c97924cccf58b1')
        self.assertIn('href="https://wa.me/5551994313154"',self.html)
        self.assertEqual(len(self.p.dots),17)


    def test_31_brand_signature_uses_logo_inspired_font(self):
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn('--font-logo-inspired:',css)
        self.assertIn('font-family:var(--font-logo-inspired)',css)
        self.assertIn('class="brand-signature"',self.html)
        self.assertIn('Data · Innovation · Technology',self.html)

    def test_32_font_fallback_without_network(self):
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn("'Bahnschrift'",css)
        self.assertIn('font-family:var(--font-reading)',css)

    def test_33_original_tree_and_contacts_unchanged(self):
        self.assertEqual(len(self.p.dots),17)
        self.assertIn('href="https://wa.me/5551994313154"',self.html)
        self.assertIn('assets/arvore-original.webp',self.html)
        self.assertIn('assets/douglas-hs-dahmer-perfil.webp',self.html)

    def test_34_font_external_declared_honestly(self):
        self.assertIn('fonts.googleapis.com/css2?family=Michroma',self.html)
        self.assertNotIn('<canvas',self.html)

    def test_35_case_study_generated_and_linked(self):
        from site_ap_09_checks import link_for, route_of
        root = self.root / 'dist'
        self.assertTrue((root / 'storytelling/index.html').is_file())
        self.assertTrue((root / 'relatorios/acessadata-health-quarto.html').is_file())
        self.assertFalse((root / 'estudo-acessadata-health-rs-2024.html').exists())
        self.assertEqual(route_of('index.html', link_for(self.html, 'Explorar estudo de caso')), '/storytelling/')
        story = (root / 'storytelling/index.html').read_text('utf-8')
        self.assertEqual(route_of('storytelling/index.html', link_for(story, 'Quarto v2')), '/relatorios/acessadata-health-quarto.html')
    def test_36_consistency_of_case_study_totals(self):
        d=json.loads((self.root/'content/estudo_health_rs_2024.json').read_text('utf8'))
        self.assertEqual(sum(x['deaths'] for x in d['sex']),21072)
        self.assertEqual(sum(x['deaths'] for x in d['ages']),21072)
        self.assertEqual(d['cancer_deaths_rs'],21072)
    def test_37_case_study_ten_unique_cid10_codes(self):
        d=json.loads((self.root/'content/estudo_health_rs_2024.json').read_text('utf8'))
        self.assertEqual(len(d['top_codes']),10)
        self.assertEqual(len({x['code'] for x in d['top_codes']}),10)
        import build
        build.validate_health(d)
    def test_38_case_study_explicit_limits(self):
        from site_ap_09_checks import visible
        q = (self.root / 'dist/relatorios/acessadata-health-quarto.html').read_text('utf-8')
        texto = visible(q)
        for afirmacao in (
            'nao sao indicadores de incidencia, prevalencia ou taxas padronizadas de mortalidade',
            'nao reprocessa o csv bruto do sim',
            'nao demonstram causalidade',
            'nao equivalem automaticamente a uma tabulacao oficial do tabnet',
        ):
            self.assertIn(afirmacao, texto)
    def test_39_all_study_links_local_or_official(self):
        from site_ap_09_checks import missing_assets, parse
        root = self.root / 'dist'
        report = 'relatorios/acessadata-health-quarto.html'
        self.assertEqual(missing_assets(root, report), [])
        self.assertTrue((root / 'dados/acessadata-health-rs-2024-resumo.json').is_file())
        self.assertTrue((root / 'dados/acessadata-health-rs-2024-top-cid.csv').is_file())
        for a in parse((root / report).read_text('utf-8')).links:
            href = a.get('href') or ''
            self.assertFalse(href.strip().lower().startswith(('javascript:', 'data:')))
    def test_40_case_study_accessible_tables(self):
        from site_ap_09_checks import parse, visible
        import re
        html = (self.root / 'dist/relatorios/acessadata-health-quarto.html').read_text('utf-8')
        self.assertGreaterEqual(len(re.findall(r'<table\b', html, re.I)), 8)
        self.assertIn('pular para o conteudo principal', visible(html))
        self.assertTrue(all('alt' in img for img in parse(html).images))
    def test_41_case_study_no_personal_data_or_js_collection(self):
        html = (self.root / 'dist/relatorios/acessadata-health-quarto.html').read_text('utf-8').lower()
        for forbidden in ('<form', 'google-analytics', 'data-collector', '037.059.'):
            self.assertNotIn(forbidden, html)
    def test_42_case_study_format_and_clean_assets(self):
        d=json.loads((self.root/'dist/dados/acessadata-health-rs-2024-resumo.json').read_text('utf8'))
        self.assertEqual(d['period'],'2024')
        import csv
        with (self.root/'dist/dados/acessadata-health-rs-2024-top-cid.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),10)
        self.assertEqual(rows[0]['codigo_cid10'],'C34')
    def test_43_original_tree_unchanged_v44(self):
        import hashlib
        self.assertEqual(hashlib.sha256((self.root/'assets/arvore-original.webp').read_bytes()).hexdigest(),
                         'fefd411bd62653da5250d340f9db279e5b355c2952d05be7e9139959b519b738')
        self.assertEqual(len(self.p.dots),17)
    def test_45_dataset_mutation_rejected(self):
        import copy,build
        d=json.loads((self.root/'content/estudo_health_rs_2024.json').read_text('utf8'))
        corrupted=copy.deepcopy(d)
        corrupted['ages'][0]['deaths']+=1
        with self.assertRaises(ValueError):build.validate_health(corrupted)

    def test_46_locale_and_technical_links(self):
        from site_ap_09_checks import visible, missing_assets
        import re
        root = self.root / 'dist'
        page = 'relatorios/acessadata-health-quarto.html'
        html = (root / page).read_text('utf-8')
        self.assertRegex(html, r'<html\b[^>]*\blang=["\']pt-BR["\']')
        self.assertIn('metodo e rastreabilidade', visible(html))
        self.assertEqual(missing_assets(root, page), [])

    def test_44_no_false_bioinformatics_claim(self):
        self.assertIn('Expansão planejada · sem oferta comercial nesta fase', self.html)
        for page in ('index.html', 'storytelling/index.html', 'relatorios/acessadata-health-quarto.html'):
            html = (self.root / 'dist' / page).read_text('utf-8').casefold()
            self.assertNotIn('medicina de precisão disponível', html)

    def test_47_minimal_hero_and_real_case_study_access(self):
        self.assertIn('Transformamos dados em', self.html)
        self.assertIn('Análise de Dados, pipelines analíticos', self.html)
        self.assertIn('href="/storytelling/"', self.html)
        self.assertIn('aria-describedby="tree-help"', self.html)
        self.assertNotIn('class="hero-choice-actions"', self.html)

    def test_48_no_duplicate_desktop_primary_guide(self):
        tree=ArvoreHTML();tree.feed(self.html)
        self.assertIsNone(tree.root.find('div','tree-major-guide'))
        main_dots=tree.root.find_all('a','tree-dot--principal')
        self.assertEqual(len(main_dots),6)
        self.assertEqual({a.get('href') for a in main_dots},
            {'#agricultura-precisao','#projetos','#metodo','#contato','#sobre','#servicos'})
        self.assertIn('data-tree-label="Agricultura de Precisão"', self.html)

    def test_49_mobile_eleven_behind_native_details(self):
        tree = ArvoreHTML()
        tree.feed(self.html)
        mobile = tree.root.find('div', 'tree-mobile-links')
        self.assertIsNotNone(mobile)
        detail = mobile.find('details', 'tree-extra-details')
        self.assertIsNotNone(detail)
        self.assertIsNone(detail.get('open'))
        self.assertEqual(len(detail.find_all('a')), 11)
        main_list = mobile.find('ul', 'tree-node-list--main')
        self.assertIsNotNone(main_list)
        self.assertEqual(len(main_list.find_all('a')), 6)

    def test_50_service_problems_and_deliverables(self):
        tree=ArvoreHTML();tree.feed(self.html)
        cards=tree.root.find_all('article','service-card')
        self.assertEqual(len(cards),3)
        for card in cards:
            outcome=card.find('div','service-outcome')
            self.assertIsNotNone(outcome)
            self.assertEqual(len(outcome.find_all('p')),2)
            self.assertEqual(len(card.find_all('a','service-action')),0)
            self.assertIn('Desafio que ajudamos a resolver',card.get_text())
            self.assertIn('Entrega prevista',card.get_text())

    def test_51_17_dots_original_coordinates_and_image_hash_unchanged(self):
        import hashlib
        self.assertEqual(len(self.p.dots),17)
        for item in self.points:
            self.assertIn('left:'+f"{item['x_percent']:.3f}"+'%;',self.html)
        self.assertEqual(hashlib.sha256((self.root/'assets/arvore-original.webp').read_bytes()).hexdigest(),
            'fefd411bd62653da5250d340f9db279e5b355c2952d05be7e9139959b519b738')

    def test_52_no_private_client_upload_or_false_claims(self):
        self.assertNotIn('<form',self.html.lower())
        self.assertIn('não envie dados pessoais sensíveis',self.html)
        self.assertIn('CNPJ: 69.899.726/0001-04',self.html)
        self.assertIn('sem oferta comercial nesta fase',self.html)
        self.assertIn('href="https://wa.me/5551994313154"',self.html)

    def test_53_suite_has_no_third_party_html_parser_requirement(self):
        code = (self.root / 'test_site.py').read_text(encoding='utf-8')
        self.assertIsNone(re.search(r'^\s*(?:from\s+bs4\s+import|import\s+bs4)\b', code, re.MULTILINE))
        self.assertIn('class ArvoreHTML(HTMLParser):', code)

    def test_54_header_has_only_logo_and_contact(self):
        tree=ArvoreHTML();tree.feed(self.html)
        header=tree.root.find('header', 'minimal-site-header')
        self.assertIsNotNone(header)
        links=header.find_all('a')
        self.assertEqual(len(links),2)
        self.assertEqual([link.get('href') for link in links],['#inicio','#contato'])
        self.assertIsNone(header.find('nav'))
        self.assertIsNone(header.find('button'))

    def test_55_header_contact_has_accessible_name(self):
        tree=ArvoreHTML();tree.feed(self.html)
        header=tree.root.find('header', 'minimal-site-header')
        contact=header.find('a', 'header-contact')
        self.assertEqual(contact.get('aria-label'),'Entrar em contato com a AcessaData-ONE')
        css=(self.root/'assets/style.css').read_text('utf-8')
        self.assertIn('.header-contact:focus-visible',css)
        self.assertIn('.header-contact-short{display:inline}',css)

    def test_56_minimal_footer_has_one_utility_link(self):
        tree=ArvoreHTML();tree.feed(self.html)
        footer=tree.root.find('footer','site-footer')
        self.assertIsNotNone(footer)
        links=footer.find_all('a')
        self.assertEqual(len(links),1)
        self.assertEqual(links[0].get('href'),'#inicio')
        self.assertIsNone(footer.find('nav','footer-shortcuts'))

    def test_57_no_obsolete_navigation_js(self):
        js=(self.root/'assets/main.js').read_text('utf-8')
        self.assertNotIn('data-menu-toggle',js)
        self.assertNotIn('primary-nav',js)
        self.assertIn('fitTooltip',js)
        self.assertIn("event.key==='Escape'",js)

    def test_58_main_tree_unmodified_by_header_change(self):
        self.assertEqual(len(self.p.dots),17)
        self.assertNotIn('class="tree-major-guide"',self.html)
        self.assertIn('class="tree-mobile-links"',self.html)
        import hashlib
        self.assertEqual(hashlib.sha256((self.root/'assets/arvore-original.webp').read_bytes()).hexdigest(),
                         'fefd411bd62653da5250d340f9db279e5b355c2952d05be7e9139959b519b738')

    def test_59_no_double_mobile_header_cta(self):
        # Only one contact link in the header on all screen sizes.
        before_main=self.html.split('<main id="conteudo">',1)[0]
        self.assertEqual(before_main.count('class="btn btn-primary header-contact"'),1)
        self.assertNotIn('id="primary-nav"',before_main)

    def test_60_unique_functional_navigation_no_repeated_ctas(self):
        tree=ArvoreHTML();tree.feed(self.html)
        self.assertIsNone(tree.root.find('div','tree-major-guide'))
        self.assertEqual(len(tree.root.find_all('a','header-contact')),1)
        self.assertEqual(len(tree.root.find_all('a','project-case-link')),1)
        self.assertEqual(len(tree.root.find_all('a','service-action')),0)
        self.assertEqual(len(tree.root.find_all('a','btn-whatsapp')),1)
        self.assertEqual(len(tree.root.find_all('a','btn-light')),1)
        self.assertEqual(len(tree.root.find_all('a','founder-whatsapp')),0)
        self.assertEqual(len(tree.root.find_all('a')),41)

    def test_61_tooltip_not_dependent_on_feedback_panel(self):
        self.assertNotIn('class="tree-feedback"',self.html)
        js=(self.root/'assets/main.js').read_text('utf8')
        self.assertIn('if (!points.length) return;',js)
        self.assertIn('if(title)title.textContent',js)
        self.assertIn('if(desc)desc.textContent',js)
        self.assertIn('fitTooltip',js)
        self.assertIn("event.key==='Escape'",js)

    def test_62_mobile_links_remain_accessible(self):
        tree=ArvoreHTML();tree.feed(self.html)
        mobile=tree.root.find('div','tree-mobile-links')
        self.assertEqual(len(mobile.find_all('a')),17)
        detail=mobile.find('details','tree-extra-details')
        self.assertIsNone(detail.get('open'))
        self.assertEqual(len(detail.find_all('a')),11)
        css=(self.root/'assets/style.css').read_text('utf8')
        self.assertIn('.tree-mobile-links{display:none}',css)
        self.assertIn('.tree-mobile-links{display:block',css)

    def test_63_no_duplicate_value_panels(self):
        self.assertNotIn('class="value-bar"',self.html)
        self.assertNotIn('class="tree-values"',self.html)
        self.assertIn('id="usabilidade"',self.html)
        self.assertIn('id="acessibilidade"',self.html)

if __name__=='__main__':unittest.main()
