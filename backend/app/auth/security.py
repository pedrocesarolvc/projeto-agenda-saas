"""
Hash de senha (Etapa 3, secao 3.2).

"No cadastro, a senha e guardada como hash (bcrypt ou argon2), nunca
em texto puro." Este arquivo e o unico lugar do backend que sabe como
gerar e conferir esse hash — assim como o filtro de tenant tem um
lugar so (core/tenancy.py), o hash de senha tambem.
"""

import bcrypt


def hash_senha(senha_texto: str) -> str:
    """Gera o hash a ser gravado em Usuario.senha_hash. Nunca reversivel."""
    hash_bytes = bcrypt.hashpw(senha_texto.encode("utf-8"), bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha_texto: str, senha_hash: str) -> bool:
    """Confere a senha digitada no login contra o hash gravado."""
    return bcrypt.checkpw(senha_texto.encode("utf-8"), senha_hash.encode("utf-8"))
