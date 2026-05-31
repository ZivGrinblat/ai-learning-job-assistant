from pydantic import BaseModel, Field


class DnaRequest(BaseModel):
    dna_string: str = Field(min_length=1, max_length=1000)

class DnaResponse(BaseModel):
    length: int
    gc_count: int
    gc_percent: float

class ComplementDnaResponse(BaseModel):
    dna_string: str
    reverse_complement: str

class NeucleotidsCounts(BaseModel):
    dna_string: str
    a: int
    t: int
    c: int
    g: int