"""Extract: baixa o .zip do INEP (com cache) e extrai os CSVs para data/extracted/<ano>/."""

import ssl
from pathlib import Path

import requests
import truststore
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from enem_pipeline.config import ENEM_URLS, RAW_DIR

CHUNK_SIZE = 1024 * 1024  # 1 MB
TIMEOUT_SECONDS = 60
INEP_HOST = "https://download.inep.gov.br/"

# o servidor do INEP derruba conexões de forma intermitente
RETRY_POLICY = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET", "HEAD"),
)


class _InepTLSAdapter(HTTPAdapter):
    """TLS 1.2 e certificados do sistema operacional.

    O servidor do INEP não suporta TLS 1.3 nem envia a cadeia completa de
    certificados (detalhes no README). Nunca usar verify=False.
    """

    def init_poolmanager(self, *args, **kwargs):
        context = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.maximum_version = ssl.TLSVersion.TLSv1_2
        kwargs["ssl_context"] = context
        return super().init_poolmanager(*args, **kwargs)


def _inep_session() -> requests.Session:
    session = requests.Session()
    session.mount(INEP_HOST, _InepTLSAdapter(max_retries=RETRY_POLICY))
    return session


def _remote_size(session: requests.Session, url: str) -> int | None:
    """Content-Length do arquivo no servidor, sem baixá-lo."""
    response = session.head(url, timeout=TIMEOUT_SECONDS, allow_redirects=True)
    response.raise_for_status()
    length = response.headers.get("Content-Length")
    return int(length) if length is not None else None


def download_zip(year: int) -> Path:
    """Baixa o .zip do ano em streaming.

    Pula o download se o arquivo local já tiver o tamanho do servidor. Grava
    num .part e só renomeia para .zip quando o download termina e o tamanho confere.
    """
    if year not in ENEM_URLS:
        anos = ", ".join(str(a) for a in sorted(ENEM_URLS))
        raise ValueError(f"Ano {year} sem URL configurada. Anos disponíveis: {anos}.")

    url = ENEM_URLS[year]
    destination = RAW_DIR / f"microdados_enem_{year}.zip"
    partial = destination.with_name(destination.name + ".part")

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    with _inep_session() as session:
        remote_size = _remote_size(session, url)

        if destination.exists() and destination.stat().st_size == remote_size:
            print(f"Cache: {destination.name} já está completo, download ignorado.")
            return destination

        size_mb = f"{remote_size / 1024**2:.0f} MB" if remote_size else "tamanho desconhecido"
        print(f"Baixando {url} ({size_mb})")
        with session.get(url, stream=True, timeout=TIMEOUT_SECONDS) as response:
            response.raise_for_status()
            with open(partial, "wb") as file:
                received = 0
                next_report = 10
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    file.write(chunk)
                    received += len(chunk)
                    if remote_size:
                        percent = received * 100 // remote_size
                        if percent >= next_report:
                            print(f"  {percent}% ({received / 1024**2:.0f} de {size_mb})")
                            next_report += 10

    downloaded = partial.stat().st_size
    if remote_size is not None and downloaded != remote_size:
        raise RuntimeError(
            f"Download incompleto: {downloaded} de {remote_size} bytes. Rode novamente."
        )

    partial.replace(destination)
    print(f"Download concluído: {destination}")
    return destination
