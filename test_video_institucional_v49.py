# -*- coding: utf-8 -*-
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class TestVideoInstitucionalV49(unittest.TestCase):
    def test_video_publicado_e_integro(self):
        src = ROOT / 'assets' / 'acessadata-arvore-institucional-web.mp4'
        dist = ROOT / 'dist' / 'assets' / src.name
        self.assertTrue(src.is_file())
        self.assertTrue(dist.is_file())
        self.assertEqual(hashlib.sha256(src.read_bytes()).digest(), hashlib.sha256(dist.read_bytes()).digest())

    def test_capa_publicada_e_integra(self):
        src = ROOT / 'assets' / 'acessadata-arvore-poster.webp'
        dist = ROOT / 'dist' / 'assets' / src.name
        self.assertTrue(src.is_file())
        self.assertTrue(dist.is_file())
        self.assertEqual(hashlib.sha256(src.read_bytes()).digest(), hashlib.sha256(dist.read_bytes()).digest())

    def test_secao_unica_e_video_sob_demanda(self):
        pagina = (ROOT / 'dist' / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(pagina.count('id="da-semente-aos-frutos"'), 1)
        self.assertIn('Da semente, aos frutos.', pagina)
        self.assertIn('controls preload="none"', pagina)
        self.assertIn('poster="assets/acessadata-arvore-poster.webp"', pagina)
        self.assertIn('assets/acessadata-arvore-institucional-web.mp4', pagina)
        self.assertIn('aria-describedby="brand-story-video-description"', pagina)
        self.assertNotIn('<video autoplay', pagina)
        self.assertLess(pagina.index('id="ecossistema"'), pagina.index('id="da-semente-aos-frutos"'))
        self.assertLess(pagina.index('id="da-semente-aos-frutos"'), pagina.index('id="servicos"'))

if __name__ == '__main__':
    unittest.main()
