import pandas as pd
import sqlite3
mileage_data = pd.read_excel("D://Documents//CRIS//1_TDL_BSP_5Month_MILEAGE_DATA.xlsx", sheet_name=None)
crew_data = pd.read_excel("D://Documents//CRIS//1_TDL_BSP_Crew_Biodata.xlsx")
slot_data = pd.read_excel("D://Documents//CRIS//Month_SLOT_DATA.xlsx")
mileage_df = pd.concat([mileage_data["TDL"], mileage_data["BSP"]], ignore_index=True)
merged_df = pd.merge(mileage_df, crew_data, on="CREW_ID_V", how="left")
merged_df["HQ_CODE_C"] = merged_df["HQ_CODE_C_x"]
merged_df = pd.merge(merged_df, slot_data, on=["SLOT_NUMBER_N", "HQ_CODE_C"], how="left")
conn = sqlite3.connect(":memory:", check_same_thread=False)
merged_df.to_sql("full_data", conn, if_exists="replace", index=False)
schema_lines = ["CREATE TABLE full_data ("]
for col, dtype in merged_df.dtypes.items():
    sql_type = "TEXT"
    if "int" in str(dtype):
        sql_type = "INTEGER"
    elif "float" in str(dtype):
        sql_type = "REAL"
    schema_lines.append(f"  {col} {sql_type},")
schema_lines[-1] = schema_lines[-1].rstrip(",")  
schema_lines.append(");")
schema = "\n".join(schema_lines)
db_conn = conn
