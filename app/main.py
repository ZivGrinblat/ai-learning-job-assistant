import argparse
import json

from app.services.text_analyzer import analyze_text

DEFAULT_SAMPLE_TEXT = (
    "This project will become an AI learning and job assistant."
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze text and print word, character, and line statistics.",
    )
    parser.add_argument(
        "--text",
        "-t",
        default=DEFAULT_SAMPLE_TEXT,
        help="Text to analyze (default: built-in sample sentence)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print raw analysis as JSON",
    )
    return parser.parse_args(argv)


def run(text: str) -> dict:
    return analyze_text(text)


def format_analysis(text: str, analysis: dict) -> str:
    lines = [
        f"Text: {text}",
        f"Words: {analysis['word_count']}",
        f"Characters: {analysis['character_count']}",
        f"Characters (no whitespace): {analysis['character_count_without_spaces']}",
        f"Lines: {analysis['line_count']}",
        f"Empty: {analysis['is_empty']}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    analysis = run(args.text)

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_analysis(args.text, analysis))


if __name__ == "__main__":
    main()
