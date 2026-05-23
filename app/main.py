from app.services.text_analyzer import count_words

def main() -> None:
    sample_text = "This project will become an AI learning and job assistant."
    word_count = count_words(sample_text)
    
    
    print(f"Text: {sample_text}")
    print(f"Word count: {word_count}")
    


if __name__ == "__main__":
    main()
    
    