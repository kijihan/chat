# api_with_model.py
# This script defines a FastAPI application to serve the trained SQL generation model
# and also executes the generated query against a pandas DataFrame.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
import json
import pandas as pd
import io
import os

# --- 1. Set up the FastAPI App ---
# Create an instance of the FastAPI application.
app = FastAPI(
    title="SQL Query Generator & Executor API",
    description="An API that generates and executes SQL queries from natural language inputs."
)

# Global variables to hold the loaded model and data
model = None
tokenizer = None
data = None
device = "cpu"

# --- 2. Load the Trained Model and Data on Startup ---
@app.on_event("startup")
def load_resources():
    """
    Loads the trained model, tokenizer, and data from CSV files when the application starts.
    This ensures that resources are ready for all subsequent requests.
    """
    global model, tokenizer, data, device
    
    # Set the device for running the model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Load the trained model and tokenizer from the local directory
    try:
        print("⏳ Loading model and tokenizer...")
        tokenizer = T5Tokenizer.from_pretrained("./trained_sql_model")
        model = T5ForConditionalGeneration.from_pretrained("./trained_sql_model").to(device)
        print("✅ Model and tokenizer loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Please ensure you have run 'train_model.py' to create the 'trained_sql_model' directory.")
        model = None
    
    # Load the XLSX data into a pandas DataFrame
    try:
        print("⏳ Loading data from Excel files...")
        excel_file = "1_TDL_BSP_5Month_MILEAGE_DATA.xlsx"
        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"File '{excel_file}' not found.")
            
        bsp_data = pd.read_excel(excel_file, sheet_name="BSP")
        tdl_data = pd.read_excel(excel_file, sheet_name="TDL")
        data = pd.concat([bsp_data, tdl_data], ignore_index=True)
        print("✅ Data loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Please ensure '1_TDL_BSP_5Month_MILEAGE_DATA.xlsx' is in the same directory and has 'BSP' and 'TDL' sheets.")
        data = None


# --- 3. Define the Request Body Structure ---
# Pydantic is used to define the data structure for the API's request body.

class QueryRequest(BaseModel):
    """
    Defines the expected format for a request to the original API endpoint.
    """
    natural_language_query: str
    schema: dict

class CrewDataRequest(BaseModel):
    """
    Defines the request for the new chatbot-like endpoint.
    The 'data_to_fetch' field acts as the menu choice.
    """
    crew_id: str
    data_to_fetch: str = Field(
        ..., 
        description="The type of data to fetch for the crew member.",
        examples=["total_duty", "total_kms", "total_trips"]
    )


# --- 4. Define the API Endpoints ---

@app.get("/")
def read_root():
    """
    A simple endpoint to confirm the API is running.
    """
    return {"message": "SQL Query Generator & Executor API is running!"}

@app.post("/generate_sql")
def generate_sql_query(request: QueryRequest):
    """
    Generates an SQL query based on a natural language input and a database schema.
    This endpoint only generates the query, it does not execute it.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded. Please ensure 'trained_sql_model' directory exists.")

    # Format the input for the model.
    input_text = f"generate sql: {request.natural_language_query} | {json.dumps(request.schema)}"
    
    # Tokenize the input string for the model
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True).to(device)
    
    # Use the model to generate an output.
    with torch.no_grad():
        outputs = model.generate(input_ids, max_length=512, num_beams=5, early_stopping=True)
    
    # Decode the generated tokens back into a string.
    generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    return {"generated_sql": generated_sql}


@app.post("/query_crew_data")
def query_crew_data(request: CrewDataRequest):
    """
    A new, chatbot-like endpoint that takes a crew ID and a specific query type from a "menu".
    It then returns the result directly by automatically generating and executing the query.
    """
    if model is None or data is None:
        raise HTTPException(status_code=500, detail="Application resources not loaded. Please check the logs.")

    # A simple mapping to translate menu choices to column names
    column_mapping = {
        "total_duty": "TOTAL_DUTY",
        "total_kms": "TOTAL_KMS",
        "total_trips": "TRIP_COUNT"
    }
    
    column_to_fetch = column_mapping.get(request.data_to_fetch.lower())
    
    if not column_to_fetch:
        raise HTTPException(status_code=400, detail="Invalid data_to_fetch value. Options are: total_duty, total_kms, total_trips.")

    # 1. Dynamically generate the schema for the model
    schema = {
        "crew_data": list(data.columns)
    }

    # 2. Formulate the natural language query for the model based on the user's input
    natural_language_query = f"What is the {request.data_to_fetch} for the crew member with ID '{request.crew_id}'?"
    
    # 3. Format the input for the model
    input_text = f"generate sql: {natural_language_query} | {json.dumps(schema)}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt", truncation=True).to(device)
    
    # 4. Generate the SQL query
    with torch.no_grad():
        outputs = model.generate(input_ids, max_length=512, num_beams=5, early_stopping=True)
    generated_sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # 5. Execute the query using pandas
    try:
        data_filtered = data[data['CREW_ID_V'] == request.crew_id]
        if data_filtered.empty:
            raise HTTPException(status_code=404, detail=f"Crew ID '{request.crew_id}' not found.")
        
        result_value = data_filtered[column_to_fetch].iloc[0]
        
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Column '{column_to_fetch}' not found in data.")
    except Exception as e:
        print(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while executing the query.")

    # 6. Return the result in a conversational format
    return {
        "response": f"The {request.data_to_fetch.replace('_', ' ')} for crew member {request.crew_id} is {result_value}."
    }
