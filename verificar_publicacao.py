"""Auditoria HTTP de leitura (sem varredura agressiva). Python >= 3.10."""
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import sys

BASE = 'https://acessadata-one.com.br'
REQUIRED = {
    'Content-Security-Policy': ["script-src 'self'", "frame-ancestors 'none'"],
    'X-Frame-Options': ['DENY'],
    'X-Content-Type-Options': ['nosniff'],
    'Referrer-Policy': ['strict-origin-when-cross-origin'],
    'Permissions-Policy': ['camera=()', 'microphone=()'],
}

def check(url):
    print('\nVerificando:',url)
    try:
        req=Request(url,headers={'User-Agent':'AcessaDataONE-auditoria-passiva/1.0'})
        with urlopen(req,timeout=15) as r:
            print('HTTP:',r.status,'| URL:',r.geturl())
            errors=[]
            if r.status!=200:errors.append('HTTP inesperado')
            for header,expected in REQUIRED.items():
                value=r.headers.get(header,'')
                ok=all(term in value for term in expected)
                print(('OK' if ok else 'FALTA'),header,':',value[:250] or 'ausente')
                if not ok: errors.append(header)
            return errors
    except (HTTPError,URLError,TimeoutError) as ex:
        print('ERRO:',ex)
        return ['acesso HTTP']

if __name__ == '__main__':
    errors=[]
    for p in ['/', '/estudo-acessadata-health-rs-2024.html']:
        errors+=check(BASE+p)
    if errors:
        print('\nATENCAO: validação incompleta ou itens ausentes:',', '.join(errors))
        print('Confira o status do deployment na Cloudflare e reexecute o script.')
        sys.exit(1)
    print('\nOK: cabeçalhos esperados encontrados nas duas páginas.')
