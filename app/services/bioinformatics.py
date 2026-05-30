def validate_dna_string(dna_string: str) -> bool:
    if len(dna_string) == 0:
        raise ValueError("DNA string cannot be shorter than 1")
    lower_case_dna_string = dna_string.lower()
    accepted_letters = ['a','g','c','t']
    for letter in lower_case_dna_string:
        if letter not in accepted_letters:
            raise ValueError("Your dna string is not valid")

def calculate_gc_content(dna_string: str): 
    validate_dna_string(dna_string)
    
    lower_case_dna_string = dna_string.lower()
    
    count_g_and_c = 0
    
    for letter in lower_case_dna_string:
        if letter == 'g' or letter == 'c':
            count_g_and_c += 1
    
    dna_string_len = len(lower_case_dna_string)
    gc_percent = (count_g_and_c / dna_string_len) * 100
    
    return {"length": dna_string_len, 
            "gc_count": count_g_and_c, 
            "gc_percent": gc_percent}
    

def return_reverse_complement_dna_string(dna_string: str):
    validate_dna_string(dna_string)
    
    lower_case_dna_string = dna_string.lower()
    
    complement_dna_string = ""
    
    for letter in lower_case_dna_string:
        if letter == 'a':
            complement_dna_string += 't'
        elif letter == 't':
            complement_dna_string += 'a'
        elif letter == 'g':
            complement_dna_string += 'c'
        else:
            complement_dna_string += 'g'
            
    reversed_complement_dna_string = complement_dna_string[::-1]
    
    return {"dna_string": lower_case_dna_string, 
            "reverse_complement": reversed_complement_dna_string}
    
    

    
    
    