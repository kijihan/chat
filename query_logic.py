# query_logic.py
import pandas as pd
from fastapi import HTTPException
from db import db_conn
from query_templates import query_templates
from nlp_model import nl_to_sql

MONTH_WHERE = "CREW_ID_V = :crew_id AND STRFTIME('%Y-%m', DATE_TIME_D) = :month"


def _needs_month(sql: str) -> bool:
    return (":month" in sql) or ("{where}" in sql)


def _finalize_sql_and_params(sql_template: str, crew_id: str, month: str | None):
    sql = sql_template
    if "{where}" in sql:
        if not month:
            raise HTTPException(status_code=400, detail="Month is required for this query")
        sql = sql.replace("{where}", MONTH_WHERE)
    params = {}
    if ":crew_id" in sql:
        params["crew_id"] = crew_id
    if ":month" in sql:
        if not month:
            raise HTTPException(status_code=400, detail="Month is required for this query")
        params["month"] = month
    return sql, params


def run_query(sql: str, params: dict) -> list[dict]:
    try:
        df = pd.read_sql_query(sql, db_conn, params=params)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_dynamic_query(domain: str, sub: str, crew_id: str, month: str | None):
    if domain not in query_templates:
        raise HTTPException(status_code=400, detail="Invalid domain")
    domain_dict = query_templates[domain]
    if sub not in domain_dict:
        raise HTTPException(status_code=400, detail=f"Invalid sub option in domain: {domain}")
    sql_template = domain_dict[sub]
    sql, params = _finalize_sql_and_params(sql_template, crew_id, month)
    return run_query(sql, params)
def run_nl_query(nl: str):
    """
    Run a free-form natural language query using the fine-tuned T5 model.
    """
    try:
        sql = nl_to_sql(nl)
        print(f"[DEBUG] Generated SQL: {sql}")
        df = pd.read_sql_query(sql, db_conn)
        return {"sql": sql, "results": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NL2SQL error: {e}")
