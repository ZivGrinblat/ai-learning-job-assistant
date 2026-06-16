"""
Pure DNA and RNA service logic — no HTTP layer, no DB access.

Input validation raises ValueError so API routes can return HTTP 422.
"""

import re
from functools import lru_cache
from typing import TypedDict

import httpx

ENZYME_SOURCE_URL = "https://raw.githubusercontent.com/Lattice-Automation/seqviz/master/src/enzymes.ts"
IUPAC_REGEX_MAP = {
    "A": "A",
    "C": "C",
    "G": "G",
    "T": "T",
    "R": "[AG]",
    "Y": "[CT]",
    "S": "[GC]",
    "W": "[AT]",
    "K": "[GT]",
    "M": "[AC]",
    "B": "[CGT]",
    "D": "[AGT]",
    "H": "[ACT]",
    "V": "[ACG]",
    "N": "[ACGT]",
}
FALLBACK_ENZYMES = {
    "EcoRI": "GAATTC",
    "HindIII": "AAGCTT",
    "BamHI": "GGATCC",
}

class GcContentResult(TypedDict):
    length: int
    gc_count: int
    gc_percent: float


class NucleotideCountsResult(TypedDict):
    dna_string: str
    a: int
    t: int
    c: int
    g: int


class ComplementResult(TypedDict):
    reverse_complement: str


class DnaComplementResult(ComplementResult):
    dna_string: str


class RnaComplementResult(ComplementResult):
    rna_string: str


class RestrictionEnzymeItem(TypedDict):
    name: str
    pattern: str


VALID_DNA = {"a", "c", "g", "t"}
VALID_RNA = {"a", "c", "g", "u"}


def _parse_enzymes_from_typescript(source_text: str) -> dict[str, str]:
    """Parse SeqViz TypeScript data into enzyme->pattern map."""
    enzymes: dict[str, str] = {}
    current_name: str | None = None
    for raw_line in source_text.splitlines():
        line = raw_line.strip()
        if line.startswith("name:"):
            name_match = re.search(r'"([^"]+)"', line)
            current_name = name_match.group(1) if name_match else None
            continue
        if current_name and line.startswith("rseq:"):
            pattern_match = re.search(r'"([^"]+)"', line)
            if pattern_match is None:
                current_name = None
                continue
            pattern = pattern_match.group(1).upper()
            if all(base in IUPAC_REGEX_MAP for base in pattern):
                enzymes[current_name] = pattern
            current_name = None
    return enzymes


@lru_cache(maxsize=1)
def get_restriction_enzymes() -> dict[str, str]:
    """Load many enzyme patterns from online source, fallback locally."""
    try:
        response = httpx.get(ENZYME_SOURCE_URL, timeout=8.0)
        response.raise_for_status()
        parsed = _parse_enzymes_from_typescript(response.text)
        if parsed:
            return parsed
    except Exception:
        pass
    return FALLBACK_ENZYMES


def get_restriction_enzymes_list() -> list[RestrictionEnzymeItem]:
    """Sorted enzyme list for frontend selectors."""
    enzymes = get_restriction_enzymes()
    return [
        {"name": name, "pattern": pattern}
        for name, pattern in sorted(enzymes.items(), key=lambda item: item[0].lower())
    ]


def find_pattern_positions(dna_string: str, pattern: str) -> list[int]:
    """Return 0-based positions where IUPAC pattern matches DNA."""
    positions = []
    dna = dna_string.upper()
    regex_pattern = "".join(IUPAC_REGEX_MAP[base] for base in pattern.upper())
    for match in re.finditer(f"(?=({regex_pattern}))", dna):
        positions.append(match.start())
    return positions


def find_restriction_sites(
    dna_string: str,
    selected_enzymes: list[str] | None = None,
) -> dict[str, list[int]]:
    """Return enzyme -> positions for selected enzymes, or all if omitted."""
    validate_dna_string(dna_string)
    all_enzymes = get_restriction_enzymes()
    if selected_enzymes:
        unknown = [name for name in selected_enzymes if name not in all_enzymes]
        if unknown:
            raise ValueError(f"Unknown enzymes: {', '.join(sorted(set(unknown)))}")
        enzymes_to_scan = {name: all_enzymes[name] for name in selected_enzymes}
    else:
        enzymes_to_scan = all_enzymes

    enzymes_dict = {}
    for name, pattern in enzymes_to_scan.items():
        enzymes_dict[name] = find_pattern_positions(dna_string, pattern)
    return enzymes_dict

def validate_dna_string(dna_string: str) -> None:
    """Raise ValueError if DNA is empty or contains non-ATGC letters."""
    if not dna_string:
        raise ValueError("DNA string cannot be shorter than 1")
    if any(letter not in VALID_DNA for letter in dna_string.lower()):
        raise ValueError("Your dna string is not valid")


def validate_rna_string(rna_string: str) -> None:
    """Raise ValueError if RNA is empty or contains non-AGCU letters."""
    if not rna_string:
        raise ValueError("RNA string cannot be shorter than 1")
    if any(letter not in VALID_RNA for letter in rna_string.lower()):
        raise ValueError("Your rna string is not valid")


def calculate_gc_content(dna_string: str) -> GcContentResult:
    """Return DNA length, GC count, and GC percentage."""
    validate_dna_string(dna_string)
    dna = dna_string.lower()
    gc_count = sum(1 for letter in dna if letter in {"g", "c"})
    length = len(dna)
    gc_percent = (gc_count / length) * 100
    return {"length": length, "gc_count": gc_count, "gc_percent": gc_percent}


def return_reverse_complement_dna_string(dna_string: str) -> DnaComplementResult:
    """Return DNA lowercase input with reverse-complement string."""
    validate_dna_string(dna_string)
    dna = dna_string.lower()
    mapping = {"a": "t", "t": "a", "g": "c", "c": "g"}
    complement = "".join(mapping[letter] for letter in dna)
    return {"dna_string": dna, "reverse_complement": complement[::-1]}


def count_nucleotides(dna_string: str) -> NucleotideCountsResult:
    """Return counts per nucleotide for validated DNA input."""
    validate_dna_string(dna_string)
    dna = dna_string.lower()
    return {
        "dna_string": dna,
        "a": dna.count("a"),
        "c": dna.count("c"),
        "t": dna.count("t"),
        "g": dna.count("g"),
    }


def return_neucleotids_counts(dna_string: str) -> NucleotideCountsResult:
    """Compatibility wrapper kept for existing imports and tests."""
    return count_nucleotides(dna_string)


def return_reverse_complement_rna_string(rna_string: str) -> RnaComplementResult:
    """Return RNA lowercase input with reverse-complement string."""
    validate_rna_string(rna_string)
    rna = rna_string.lower()
    mapping = {"a": "u", "u": "a", "g": "c", "c": "g"}
    complement = "".join(mapping[letter] for letter in rna)
    return {"rna_string": rna, "reverse_complement": complement[::-1]}
