"""
Pydantic models for DNA bio endpoints.

DnaRequest is shared by all three POST /bio/* routes.
Each response model matches one service return shape.
"""

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

class RnaRequest(BaseModel):
    rna_string: str = Field(min_length=1, max_length=1000)
class ComplementRnaResponse(BaseModel):
    rna_string: str
    reverse_complement: str