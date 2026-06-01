import pytest

from app.services.bioinformatics import (
    return_reverse_complement_dna_string,
    return_reverse_complement_rna_string,
    validate_rna_string,
)


def test_return_reverse_complement_dna_string():
    result = return_reverse_complement_dna_string("AAGGCCA")

    assert result["reverse_complement"] == "tggcctt"
    assert result["dna_string"] == "aaggcca"


def test_return_reverse_complement_rna_string():
    result = return_reverse_complement_rna_string("aauuggc")

    assert result["reverse_complement"] == "gccaauu"


def test_validate_rna_string_rejects_dna_letters():
    with pytest.raises(ValueError, match="not valid"):
        validate_rna_string("ATCG")


def test_validate_rna_string_rejects_empty():
    with pytest.raises(ValueError, match="shorter than 1"):
        validate_rna_string("")


def test_return_reverse_complement_rna_string_rejects_invalid_input():
    with pytest.raises(ValueError):
        return_reverse_complement_rna_string("AAD")
