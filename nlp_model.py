# nlp_model.py
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

#  Path to your fine-tuned model
MODEL_DIR = "D:/Music/t5_sql_finetuned"  # ✅ Use forward slashes or raw string


# Load tokenizer + model once
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

def nl_to_sql(nl_query: str) -> str:
    """
    Convert natural language query into SQL using fine-tuned T5.
    """
    inp = f"NL2SQL: {nl_query}"
    inputs = tokenizer([inp], return_tensors="pt", truncation=True).to(device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=128)
    sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql

