import threading
import contextvars
import psycopg2
from app.config import DATABASE_URL

_lock = threading.Lock()
_conexao_escrita_turno: contextvars.ContextVar[psycopg2.extensions.connection | None] = (
    contextvars.ContextVar("_conexao_escrita_turno", default=None)
)
_conexao_global_turno = None

def get_conn():
    """Conexão pontual usada para leituras (consultas/saldos)."""
    return psycopg2.connect(DATABASE_URL)

def obter_conexao_escrita():
    """
    Retorna a conexão de escrita compartilhada do turno atual.
    A transação permanece aberta até a decisão do juiz.
    """
    global _conexao_global_turno
    conn = _conexao_escrita_turno.get()
    if conn is None or conn.closed:
        with _lock:
            if _conexao_global_turno is None or _conexao_global_turno.closed:
                _conexao_global_turno = psycopg2.connect(DATABASE_URL)
                _conexao_global_turno.autocommit = False
            conn = _conexao_global_turno
        _conexao_escrita_turno.set(conn)
    return conn

def confirmar_transacao_turno() -> bool:
    """Executa commit e fecha a conexão se houver transação aberta."""
    global _conexao_global_turno
    conn = _conexao_escrita_turno.get() or _conexao_global_turno
    if conn and not conn.closed:
        try:
            conn.commit()
            print("[db] Transação confirmada com sucesso (commit)!")
            return True
        finally:
            conn.close()
            _conexao_escrita_turno.set(None)
            _conexao_global_turno = None
    return False

def descartar_transacao_turno() -> bool:
    """Executa rollback e fecha a conexão se houver transação aberta."""
    global _conexao_global_turno
    conn = _conexao_escrita_turno.get() or _conexao_global_turno
    if conn and not conn.closed:
        try:
            conn.rollback()
            print("[db] Transação descartada com sucesso (rollback)!")
            return True
        finally:
            conn.close()
            _conexao_escrita_turno.set(None)
            _conexao_global_turno = None
    return False
