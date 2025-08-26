# main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from auth import authenticate_user, create_access_token, verify_token
from models import QueryRequest, NaturalQueryRequest
from query_logic import run_dynamic_query, run_nl_query
from db import db_conn
import pandas as pd

app = FastAPI(title="Crew Chatbot API")

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/query")
def query_info(request: QueryRequest, username: str = Depends(verify_token)):
    return run_dynamic_query(request.domain, request.sub, request.crew_id, request.month)


@app.post("/nlquery")
def natural_language_query(request: NaturalQueryRequest, username: str = Depends(verify_token)):
    """
     Default: Try fine-tuned T5 NL2SQL model first
     Fallback: keyword → dynamic query
    """
    if not request.crew_id or not request.query:
        raise HTTPException(status_code=400, detail="crew_id and query are required")

    # --- Use fine-tuned model as primary ---
    try:
        return run_nl_query(request.query)
    except Exception as e:
        print(f"[DEBUG] run_nl_query failed: {e}")

    # --- Fallback: keyword-based ---
    query_text = request.query.lower()
    if "total kms" in query_text or "kms" in query_text:
        return run_dynamic_query("3", "1", request.crew_id, request.month)
    elif "footplate" in query_text:
        return run_dynamic_query("3", "2", request.crew_id, request.month)
    elif "leave" in query_text:
        return run_dynamic_query("1", "5", request.crew_id, request.month)
    elif "night" in query_text:
        return run_dynamic_query("2", "7", request.crew_id, request.month)

    return {
        "fallback": True,
        "message": "Could not interpret query. Try rephrasing or use menu options."
    }
#uvicorn main:app --reload
