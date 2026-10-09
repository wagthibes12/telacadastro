
import bcrypt


def hash_senha(senha_texto_plano: str) -> str:
    senha_bytes = senha_texto_plano.encode("utf-8")
    hash_bytes = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_texto_plano: str, hash_armazenado: str) -> bool:
    return bcrypt.checkpw(
        senha_texto_plano.encode("utf-8"), hash_armazenado.encode("utf-8")
    )