"""
Pydantic models for DNA bio endpoints.

DnaRequest is shared by all three POST /bio/* routes.
Each response model matches one service return shape.
"""

from pydantic import BaseModel, Field


class RestrictionsResponse(BaseModel):
    """Restriction scan result: enzyme names mapped to match positions."""
    dna_string: str
    sites: dict[str, list[int]]


class RestrictionSitesRequest(BaseModel):
    """DNA input and optional enzyme subset for targeted scanning."""
    dna_string: str = Field(min_length=1, max_length=1000)
    selected_enzymes: list[str] | None = None


class RestrictionEnzymeItem(BaseModel):
    """One enzyme option with its recognition pattern."""
    name: str
    pattern: str


class RestrictionEnzymesResponse(BaseModel):
    """Catalog of available enzymes loaded from source data."""
    source: str
    count: int
    enzymes: list[RestrictionEnzymeItem]


class DnaRequest(BaseModel):
    """Input payload for DNA-based endpoints."""
    dna_string: str = Field(min_length=1, max_length=1000)


class DnaResponse(BaseModel):
    """GC-content calculation response."""
    length: int
    gc_count: int
    gc_percent: float


class ComplementDnaResponse(BaseModel):
    """DNA reverse-complement response."""
    dna_string: str
    reverse_complement: str


class NeucleotidsCounts(BaseModel):
    """Legacy name kept for compatibility with existing route imports."""
    dna_string: str
    a: int
    t: int
    c: int
    g: int


class NucleotidesCounts(NeucleotidsCounts):
    """Preferred spelling alias for future internal readability."""


class RnaRequest(BaseModel):
    """Input payload for RNA-based endpoints."""
    rna_string: str = Field(min_length=1, max_length=1000)


class ComplementRnaResponse(BaseModel):
    """RNA reverse-complement response."""
    rna_string: str
    reverse_complement: str