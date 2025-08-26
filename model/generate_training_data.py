# generate_training_data.py
# This script creates a synthetic dataset for training a Seq2Seq model.

import pandas as pd
import random
import json
from typing import Dict, Any

# Define the full set of all possible menu choices
SELECT_COLUMNS = ["CREW_ID_V", "TOTAL_KMS", "TOTAL_DUTY", "RUN_DUTY_MIN", "NON_RUN_DUTY_MIN"]
HQ_CODES = ["TDL", "BSP", None]
SORT_BYS = ["TOTAL_KMS", "TOTAL_DUTY", None]
SORT_ORDERS = ["ASC", "DESC", None]

# Define valid numeric ranges for filters. These are based on your file data.
NUMERIC_RANGES = {
    "TOTAL_KMS": (100, 10000),
    "TOTAL_DUTY": (1000, 15000),
    "RUN_DUTY_MIN": (500, 15000),
    "NON_RUN_DUTY_MIN": (0, 5000)
}

def generate_sql_query(options: Dict[str, Any]) -> str:
    """
    This is our rule-based engine. It takes a dictionary of options and
    returns a perfectly formed SQL query. The model will learn to mimic this logic.
    """
    table_map = {"TDL": "TDL_MILEAGE_DATA", "BSP": "BSP_MILEAGE_DATA"}
    query_parts = []
    
    select_column = options.get('select_column')
    if select_column:
        query_parts.append(f"SELECT {select_column}")

    hq_code = options.get('hq_code')
    table_name = table_map.get(hq_code, "CREW_MILEAGE_DATA")
    query_parts.append(f"FROM {table_name}")

    where_conditions = []
    if hq_code:
        where_conditions.append(f"HQ_CODE_C = '{hq_code}'")

    min_val = options.get('min_value')
    max_val = options.get('max_value')
    if min_val is not None or max_val is not None:
        if select_column in NUMERIC_RANGES:
            if min_val is not None and max_val is not None:
                where_conditions.append(f"{select_column} BETWEEN {min_val} AND {max_val}")
            elif min_val is not None:
                where_conditions.append(f"{select_column} >= {min_val}")
            elif max_val is not None:
                where_conditions.append(f"{select_column} <= {max_val}")

    if where_conditions:
        query_parts.append("WHERE " + " AND ".join(where_conditions))

    sort_by = options.get('sort_by')
    if sort_by:
        sort_order = "DESC" if options.get('sort_order', 'ASC').upper() == "DESC" else "ASC"
        query_parts.append(f"ORDER BY {sort_by} {sort_order}")
    
    return " ".join(query_parts) + ";"

# Generate 10,000 synthetic data examples
training_data = []
for _ in range(10000):
    # Randomly select options for each field
    options = {
        "select_column": random.choice(SELECT_COLUMNS),
        "hq_code": random.choice(HQ_CODES),
        "sort_by": random.choice(SORT_BYS),
        "sort_order": random.choice(SORT_ORDERS)
    }
    
    # Add optional numeric filters
    column_for_filter = random.choice(list(NUMERIC_RANGES.keys()) + [None])
    if column_for_filter:
        min_v, max_v = NUMERIC_RANGES[column_for_filter]
        if random.random() > 0.5:  # 50% chance to have a min_value
            options['min_value'] = random.randint(min_v, max_v)
        if random.random() > 0.5:  # 50% chance to have a max_value
            options['max_value'] = random.randint(min_v, max_v)

    # Clean up the options dictionary by removing None values for cleaner input
    clean_options = {k: v for k, v in options.items() if v is not None}
    
    # Generate the SQL query from the clean options
    sql_query = generate_sql_query(clean_options)
    
    # The input for the model is a stringified JSON of the menu options.
    input_string = json.dumps(clean_options, sort_keys=True)
    training_data.append({"input": input_string, "output": sql_query})

# Save the generated data to a CSV file
df = pd.DataFrame(training_data)
df.to_csv("training_data.csv", index=False)
print("✅ Training data generated and saved to training_data.csv!")