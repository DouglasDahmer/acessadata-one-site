"""Release-specific tests: security, navigation, assets, and data integrity."""
import copy
import json
from pathlib import Path
import unittest
from site_ap_09_checks import link_for, route_of, parse, missing_assets, visible
import build

ROOT = Path(__file__).parent
DIST = ROOT / 'dist'


class TestSiteSimplificado(unittest.TestCase):
    def test_01_somente_tres_paginas_html(self):
        atual = {p.relative_to(DIST).as_posix() for p in DIST.rglob('*.html')}
        self.assertEqual(atual, {
            'index.html', 'storytelling/index.html',
            'relatorios/acessadata-health-quarto.html',
        })

    def test_02_navegacao_home_story_quarto(self):
        home = (DIST / 'index.html').read_text('utf-8')
        story = (DIST / 'storytelling/index.html').read_text('utf-8')
        self.assertEqual(route_of('index.html', link_for(home, 'Explorar estudo de caso')), '/storytelling/')
        self.assertEqual(route_of('storytelling/index.html', link_for(story, 'Quarto v2')), '/relatorios/acessadata-health-quarto.html')

    def test_03_redirects_legados_preservados(self):
        regras = (DIST / '_redirects').read_text('utf-8').splitlines()
        self.assertEqual(regras, [
            '/estudo-acessadata-health-rs-2024 /relatorios/acessadata-health-quarto 301',
            '/estudo-acessadata-health-rs-2024.html /relatorios/acessadata-health-quarto 301',
            '/relatorios/quarto-v1 /relatorios/acessadata-health-quarto 301',
            '/relatorios/quarto-v1/ /relatorios/acessadata-health-quarto 301',
            '/relatorios/quarto-v1/index.html /relatorios/acessadata-health-quarto 301',
        ])

    def test_04_sem_scripts_inline_nas_tres_paginas(self):
        import re
        for page in ('index.html', 'storytelling/index.html', 'relatorios/acessadata-health-quarto.html'):
            html = (DIST / page).read_text('utf-8')
            scripts = re.findall(r'<script\b([^>]*)>(.*?)</script>', html, re.I | re.S)
            self.assertTrue(all('src=' in attrs and not body.strip() for attrs, body in scripts), page)

    def test_05_recursos_necessarios_presentes(self):
        for page in ('index.html', 'storytelling/index.html', 'relatorios/acessadata-health-quarto.html'):
            self.assertEqual(missing_assets(DIST, page), [], page)

    def test_06_validacao_epidemiologica_rejeita_mutacao(self):
        dados = json.loads((ROOT / 'content/estudo_health_rs_2024.json').read_text('utf-8'))
        self.assertEqual(dados['cancer_deaths_rs'], 21072)
        self.assertEqual(sum(x['deaths'] for x in dados['sex']), 21072)
        self.assertEqual(sum(x['deaths'] for x in dados['ages']), 21072)
        self.assertEqual(len({x['code'] for x in dados['top_codes']}), 10)
        build.validate_health(dados)
        mutado = copy.deepcopy(dados)
        mutado['ages'][0]['deaths'] += 1
        with self.assertRaises(ValueError):
            build.validate_health(mutado)

    def test_07_csp_e_configuracoes_presentes(self):
        h = (DIST / '_headers').read_text('utf-8')
        self.assertIn("script-src 'self';", h)
        self.assertIn("object-src 'none';", h)
        self.assertIn('X-Content-Type-Options: nosniff', h)
        self.assertTrue((DIST / '_redirects').is_file())

    def test_08_quarto_interpretacao_responsavel(self):
        report = visible((DIST / 'relatorios/acessadata-health-quarto.html').read_text('utf-8'))
        self.assertIn('nao demonstram causalidade', report)
        self.assertIn('nao reprocessa o csv bruto do sim', report)
        self.assertIn('nao equivalem automaticamente a uma tabulacao oficial do tabnet', report)
