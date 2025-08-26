from pydantic import BaseModel
class QueryRequest(BaseModel):
    crew_id: str
    month: str
    domain: str
    sub: str
class NaturalQueryRequest(BaseModel):
    crew_id: str
    month: str
    query: str
