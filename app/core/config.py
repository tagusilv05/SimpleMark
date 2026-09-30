# Arquivo criado por Victor
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parâmetros de execução da API.

    Valores lidos do ambiente ou do arquivo .env. O arquivo
    .env.example lista o que precisa existir na máquina de cada integrante.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ambiente: str = "desenvolvimento"
    secret_key: str = "troque-esta-chave-antes-de-subir-o-sistema"
    database_url: str = "postgresql+psycopg://simplemark:simplemark@localhost:5432/simplemark"
    cors_origens: str = "http://localhost:5173"

    @property
    def lista_cors(self) -> list[str]:
        """Separa as origens do CORS que o navegador pode chamar.

        Passo a passo:
        1. Corta cors_origens nas vírgulas.
        2. Tira o espaço de cada pedaço.
        3. Descarta pedaço vazio e devolve a lista usada no middleware.
        """
        return [origem.strip() for origem in self.cors_origens.split(",") if origem.strip()]


@lru_cache
def get_settings() -> Settings:
    """Lê o .env uma vez e reaproveita o mesmo objeto no resto do processo.

    Passo a passo:
    1. Na primeira chamada, o Pydantic lê variáveis de ambiente e o arquivo .env.
    2. O lru_cache guarda o resultado.
    3. As chamadas seguintes devolvem o mesmo Settings, sem reler o arquivo.
    """
    return Settings()


settings = get_settings()
