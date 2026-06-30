"""Usuario model — parametrized SQL and password hashing.

Serialization never includes `senha`. Authentication fetches the user by
email and verifies the stored hash with werkzeug; passwords are stored hashed
(see database.connection seed) and created hashed.
"""
from werkzeug.security import check_password_hash, generate_password_hash

from database.connection import get_db


def _serialize(row):
    """Public representation of a user — no senha (sensitive)."""
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_todos():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_serialize(row) for row in cursor.fetchall()]


def get_por_id(usuario_id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    return _serialize(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    """Return the public user dict if the password matches, else None."""
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row and check_password_hash(row["senha"], senha):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
    return None


def contar():
    cursor = get_db().cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    return cursor.fetchone()[0]
