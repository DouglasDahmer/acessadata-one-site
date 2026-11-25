"""Verificações regressivas de segurança do site. Somente biblioteca padrão."""
from pathlib import Path
import re
import unittest
import build

ROOT=Path(__file__).resolve().parent

class TesteSegurancaV48(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The clean build is executed and hashed before unittest.
        cls.headers=(ROOT/'dist'/'_headers').read_text(encoding='utf8')
        cls.html=(ROOT/'dist'/'index.html').read_text(encoding='utf8')
        cls.pages=[(ROOT/'dist'/p).read_text(encoding='utf8') for p in ('index.html','storytelling/index.html','relatorios/acessadata-health-quarto.html')]

    def test_01_arquivo_headers_publicado(self):
        self.assertTrue((ROOT/'dist'/'_headers').is_file())

    def test_02_csp_restringe_scripts_ao_site(self):
        self.assertIn("script-src 'self';",self.headers)
        self.assertIn("object-src 'none';",self.headers)
        self.assertIn("base-uri 'self';",self.headers)
        self.assertIn("frame-ancestors 'none';",self.headers)
        self.assertNotIn("script-src 'unsafe-inline'",self.headers)
        self.assertNotIn("script-src 'unsafe-eval'",self.headers)

    def test_03_csp_permite_fontes_existentes(self):
        self.assertIn("https://fonts.googleapis.com",self.headers)
        self.assertIn("https://fonts.gstatic.com",self.headers)

    def test_04_csp_restringe_estilos_elementos(self):
        self.assertIn("style-src-elem 'self' https://fonts.googleapis.com;",self.headers)
        self.assertIn("style-src-attr 'unsafe-inline';",self.headers)

    def test_05_protecao_frame_mime_referrer(self):
        self.assertIn('X-Frame-Options: DENY',self.headers)
        self.assertIn('X-Content-Type-Options: nosniff',self.headers)
        self.assertIn('Referrer-Policy: strict-origin-when-cross-origin',self.headers)

    def test_06_permissoes_bloqueadas(self):
        for f in ['camera=()', 'microphone=()', 'geolocation=()', 'payment=()']:
            self.assertIn(f,self.headers)

    def test_07_html_sem_scripts_inline(self):
        scripts=re.findall(r'<script([^>]*)>(.*?)</script>',self.html,re.I|re.S)
        self.assertTrue(scripts)
        self.assertTrue(all('src=' in attrs and not body.strip() for attrs,body in scripts))
        self.assertNotRegex(self.html,r'\bon(?:click|load|error)\s*=')

    def test_08_links_externos_nova_aba_protegidos(self):
        import re
        for html in self.pages:
            for tag in re.findall(r'<a\b[^>]*target=["\']_blank["\'][^>]*>', html, re.I):
                self.assertRegex(tag, r'rel=["\'][^"\']*noopener')

    def test_09_sem_configuracoes_sensiveis_publicadas(self):
        files={x.name for x in (ROOT/'dist').iterdir()}
        for forbidden in ['.env','.git','config.json','wrangler.toml','id_rsa','.htpasswd']:
            self.assertNotIn(forbidden,files)

    def test_10_endpoints_de_dados_agregados_preservados(self):
        self.assertTrue((ROOT/'dist'/'dados'/'acessadata-health-rs-2024-resumo.json').exists())
        self.assertTrue((ROOT/'dist'/'dados'/'acessadata-health-rs-2024-top-cid.csv').exists())

    def test_11_navegacao_e_logo_preservados(self):
        self.assertEqual(len(re.findall(r'<a class="tree-dot\s',self.html)),17)
        self.assertIn('assets/arvore-original.webp',self.html)
        self.assertIn('class="tree-mobile-links"',self.html)

    def test_12_dominio_pages_dev_nao_indexavel(self):
        self.assertIn('https://acessadata-one.pages.dev/*',self.headers)
        self.assertIn('X-Robots-Tag: noindex',self.headers)

if __name__ == '__main__':
    unittest.main()
