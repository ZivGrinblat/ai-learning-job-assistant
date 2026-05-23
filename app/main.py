from app.services.text_analyzer import analyze_text

# Change this string to try different text, or use the exercise below.
SAMPLE_TEXT = "This project will become an AI learning and job assistant."


def run(text: str) -> dict:
    """Run analysis on text. Returns the same dict as analyze_text."""
    return analyze_text(text)


def format_analysis(text: str, analysis: dict) -> str:
    """Turn analysis dict into text you can print."""
    lines = [
        f"Text: {text}",
        f"Words: {analysis['word_count']}",
        f"Characters: {analysis['character_count']}",
        f"Characters (no whitespace): {analysis['character_count_without_spaces']}",
        f"Lines: {analysis['line_count']}",
        f"Empty: {analysis['is_empty']}",
    ]
    return "\n".join(lines)


def main(text: str | None = None) -> None:
    text_to_analyze = SAMPLE_TEXT if text is None else text
    analysis = run(text_to_analyze)
    print(format_analysis(text_to_analyze, analysis))


if __name__ == "__main__":
    main()

    # --- Your turn (pick one when ready; delete or comment out after trying) ---
    # 1) Ask the user:  text_to_analyze = input("Enter text to analyze: ")
    # 2) First CLI arg:  import sys
    #                    text_to_analyze = sys.argv[1]   # run: python -m app.main "hello"
    # 3) Later chapter:  argparse (--help, --text flags) — learn when you want flags
