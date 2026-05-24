import argparse

from app.services.text_analyzer import analyze_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze text and return basic statistics."
    )

    parser.add_argument(
        "text",
        help="The text to analyze.",
    )

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    result = analyze_text(args.text)

    print(f"Text: {args.text}")
    print(f"Word count: {result['word_count']}")
    print(f"Character count: {result['character_count']}")
    print(f"Character count without spaces: {result['character_count_without_spaces']}")
    print(f"Line count: {result['line_count']}")
    print(f"Is empty: {result['is_empty']}")


if __name__ == "__main__":
    main()