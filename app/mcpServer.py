import sys
from pathlib import Path
from typing import Annotated, Any, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from app.tools.financeiro import (
    add_transaction as _add_transaction,
    consultar_perfil_usuario as _consultar_perfil_usuario,
    list_categories as _list_categories,
    saldo_diario as _saldo_diario,
    saldo_total as _saldo_total,
    search_transactions as _search_transactions,
    update_transaction as _update_transaction,
)

mcp = MCPServer(
    name="assessor-financeiro",
    version="1.0.0",
    instructions="Ferramentas financeiras do Assessor.AI...",
)

LEITURA = ToolAnnotations(readOnlyHint=True)
ESCRITA = ToolAnnotations(readOnlyHint=False, destructiveHint=False)

@mcp.tool(
    name="total_balance",
    title="Saldo total",
    description="Saldo de todo o histórico: receitas menos despesas.",
    annotations=LEITURA,
)
def total_balance() -> dict[str, Any]:
    return _saldo_total.invoke({})


@mcp.tool(
    name="daily_balance",
    title="Saldo diário",
    description="Saldo do dia atual: receitas menos despesas.",
    annotations=LEITURA,
)
def daily_balance() -> dict[str, Any]:
    return _saldo_diario.invoke({})


@mcp.tool(
    name="query_transactions",
    title="Buscar transações",
    description="Busca transações por texto em sua descrição ou texto original.",
    annotations=LEITURA,
)
def query_transactions(
    query: Annotated[str, Field(description="Texto parcial para buscar.")],
    limit: Annotated[Optional[int], Field(description="Número máximo de resultados.")] = 10,
) -> dict[str, Any]:
    return _search_transactions.invoke({"query": query, "limit": limit})


@mcp.tool(
    name="add_transaction",
    title="Inserir transação",
    description="Insere uma transação na tabela transactions.",
    annotations=ESCRITA,
)
def add_transaction(
    amount: Annotated[float, Field(description="Valor (sempre positivo).")],
    source_text: Annotated[str, Field(description="Texto original.")],
    type_name: Annotated[Optional[str], Field(description="INCOME | EXPENSES | TRANSFER")] = None,
    category_name: Annotated[Optional[str], Field(description="Categoria em pt-BR.")] = None,
    occurred_at: Annotated[Optional[str], Field(description="Data da transação (YYYY-MM-DD).")] = None,
    description: Annotated[Optional[str], Field(description="Descrição da transação.")] = None,
    payment_method: Annotated[Optional[str], Field(description="Método de pagamento.")] = None,
) -> dict[str, Any]:
    return _add_transaction.invoke({
        "amount": amount,
        "source_text": source_text,
        "type_name": type_name,
        "category_name": category_name,
        "occurred_at": occurred_at,
        "description": description,
        "payment_method": payment_method,
    })


@mcp.tool(
    name="update_transaction",
    title="Atualizar transação",
    description="Atualiza uma transação existente por ID ou por texto e data local.",
    annotations=ESCRITA,
)
def update_transaction(
    id: Annotated[Optional[int], Field(description="ID da transação.")] = None,
    match_text: Annotated[Optional[str], Field(description="Texto para localizar a transação.")] = None,
    date_local: Annotated[Optional[str], Field(description="Data local YYYY-MM-DD.")] = None,
    amount: Annotated[Optional[float], Field(description="Novo valor.")] = None,
    type_name: Annotated[Optional[str], Field(description="INCOME | EXPENSES | TRANSFER.")] = None,
    category_name: Annotated[Optional[str], Field(description="Novo nome da categoria.")] = None,
    description: Annotated[Optional[str], Field(description="Nova descrição.")] = None,
    payment_method: Annotated[Optional[str], Field(description="Novo método de pagamento.")] = None,
    occurred_at: Annotated[Optional[str], Field(description="Novo timestamp ISO 8601.")] = None,
) -> dict[str, Any]:
    return _update_transaction.invoke({
        "id": id,
        "match_text": match_text,
        "date_local": date_local,
        "amount": amount,
        "type_name": type_name,
        "category_name": category_name,
        "description": description,
        "payment_method": payment_method,
        "occurred_at": occurred_at,
    })


if __name__ == "__main__":
    from app.config import DATABASE_URL

    if not DATABASE_URL:
        print("[assessor-financeiro]: DATABSE_URL não presente no .env", file=sys.stderr)

    mcp.run(transport="stdio")