# coding: utf-8
"""Testes adicionais da apresentação pública da v4.9."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class TestPortfolioV49(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / 'dist' / 'index.html').read_text(encoding='utf-8')
        cls.site = json.loads((ROOT / 'content' / 'site.json').read_text(encoding='utf-8'))
        cls.mapa = json.loads((ROOT / 'content' / 'mapa_circulos.json').read_text(encoding='utf-8'))

    def test_fundador_publico_abreviado(self):
        self.assertEqual(self.site['founder'], 'Douglas H.S. Dahmer')
        self.assertIn('Douglas H.S. Dahmer', self.html)
        self.assertNotIn('Douglas Henrique Silveira Dahmer', self.html)

    def test_empresa_inova_simples_cnpj(self):
        self.assertIn('69.899.726/0001-04', self.html)
        self.assertIn('ACESSADATA-ONE INOVA SIMPLES (I.S.)', self.html)
        self.assertNotIn('fase de formalização', self.html)

    def test_programas_ainda_nao_divulgados(self):
        for nome in ('AcessaData IDE', 'AcessaDataAI'):
            self.assertNotIn(nome, self.html)
            self.assertNotIn(nome, [p.get('name') for p in self.site['projects']])
            self.assertNotIn(nome, [p['titulo'] for p in self.mapa['pontos']])

    def test_foto_local_e_acessivel(self):
        self.assertIn('src="assets/douglas-hs-dahmer-perfil.webp"', self.html)
        self.assertIn('alt="Retrato de Douglas H.S. Dahmer"', self.html)
        self.assertTrue((ROOT / 'dist' / 'assets' / 'douglas-hs-dahmer-perfil.webp').is_file())

    def test_projeto_health_preservado(self):
        self.assertIn('AcessaData-Health', self.html)
        self.assertIn('href="/storytelling/"', self.html)
        self.assertTrue((ROOT / 'dist' / 'storytelling/index.html').is_file())
        self.assertTrue((ROOT / 'dist' / 'relatorios/acessadata-health-quarto.html').is_file())

    def test_mapa_17_circulos_sem_expor_programas(self):
        pontos = self.mapa['pontos']
        self.assertEqual(len(pontos), 17)
        self.assertEqual(len(set(p['destino_planejado'] for p in pontos)), 17)
        self.assertIn('id="visao-futuro"', self.html)
        self.assertIn('href="#visao-futuro"', self.html)
        self.assertIn('href="#ecossistema"', self.html)

    def test_sem_dados_pessoais_do_certificado(self):
        # Evita publicar por engano os identificadores pessoais ou o documento integral.
        self.assertNotIn('037.059.880-69', self.html)
        self.assertNotIn('RUA JADE', self.html.upper())
        self.assertNotIn('Certificado de Inova Simples.pdf', self.html)

if __name__ == '__main__':
    unittest.main()
