"""
Pure DNA and RNA strings logic — no HTTP, no database.

Invalid input raises ValueError; routes catch and return 422.
All functions return dicts that match bio schema fields.
"""


def validate_dna_string(dna_string: str) -> None:
    """Raise ValueError if empty or contains non-ATGC letters."""
    if len(dna_string) == 0:
        raise ValueError("DNA string cannot be shorter than 1")
    lower_case_dna_string = dna_string.lower()
    accepted_letters = ["a", "g", "c", "t"]
    for letter in lower_case_dna_string:
        if letter not in accepted_letters:
            raise ValueError("Your dna string is not valid")

def validate_rna_string(rna_string: str) -> None:
    """Raise ValueError if empty or contains non-AGCU letters"""
    if len(rna_string) == 0:
        raise ValueError("RNA string cannot be shorter than 1")
    lower_cased_rna_string = rna_string.lower()
    accepted_letters = ["a", "g", "c", "u"]
    for letter in lower_cased_rna_string:
        if letter not in accepted_letters:
            raise ValueError("Your rna string is not valid")
        

def calculate_gc_content(dna_string: str) -> dict:
    validate_dna_string(dna_string)

    lower_case_dna_string = dna_string.lower()

    count_g_and_c = 0

    for letter in lower_case_dna_string:
        if letter == "g" or letter == "c":
            count_g_and_c += 1

    dna_string_len = len(lower_case_dna_string)
    gc_percent = (count_g_and_c / dna_string_len) * 100

    return {
        "length": dna_string_len,
        "gc_count": count_g_and_c,
        "gc_percent": gc_percent,
    }


def return_reverse_complement_dna_string(dna_string: str) -> dict:
    validate_dna_string(dna_string)

    lower_case_dna_string = dna_string.lower()

    complement_dna_string = ""

    for letter in lower_case_dna_string:
        if letter == "a":
            complement_dna_string += "t"
        elif letter == "t":
            complement_dna_string += "a"
        elif letter == "g":
            complement_dna_string += "c"
        else:
            complement_dna_string += "g"

    reversed_complement_dna_string = complement_dna_string[::-1]

    return {
        "dna_string": lower_case_dna_string,
        "reverse_complement": reversed_complement_dna_string,
    }



def return_neucleotids_counts(dna_string: str) -> dict:
    validate_dna_string(dna_string)

    lower_case_dna_string = dna_string.lower()

    a_count = 0
    c_count = 0
    g_count = 0
    t_count = 0

    for letter in lower_case_dna_string:
        if letter == "a":
            a_count += 1
        elif letter == "c":
            c_count += 1
        elif letter == "g":
            g_count += 1
        else:
            t_count += 1
    return {
        "dna_string": lower_case_dna_string,
        "a": a_count,
        "c": c_count,
        "t": t_count,
        "g": g_count,
    }

def return_reverse_complement_rna_string(rna_string: str) -> dict:
    validate_rna_string(rna_string)
    lower_cased_rna_string = rna_string.lower()
    complement_rna_string = ""
    for letter in lower_cased_rna_string:
        if letter == 'a':
            complement_rna_string += 'u'
        elif letter == 'u':
            complement_rna_string += 'a'
        elif letter == 'g':
            complement_rna_string += 'c'
        else:
            complement_rna_string += 'g'
            
    reversed_complement_rna_string = complement_rna_string[::-1]
    return {"rna_string": lower_cased_rna_string,  "reverse_complement": reversed_complement_rna_string}
