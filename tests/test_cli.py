import pytest

from app.cli import build_parser, main
from app.services.text_analyzer import analyze_text


def test_build_parser_requires_text_argument():
    parser = build_parser()
    args = parser.parse_args(["Hello world"])

    assert args.text == "Hello world"


def test_main_prints_analysis_stats(capsys):
    main(["Hello world"])
    captured = capsys.readouterr()

    assert "Text: Hello world" in captured.out
    assert "Word count: 2" in captured.out
    assert "Character count: 11" in captured.out
    assert "Character count without spaces: 10" in captured.out
    assert "Line count: 1" in captured.out
    assert "Is empty: False" in captured.out


def test_main_uses_analyze_text(capsys):
    text = "Hello world"
    main([text])
    captured = capsys.readouterr()

    result = analyze_text(text)
    assert f"Word count: {result['word_count']}" in captured.out


def test_parse_args_accepts_text_with_spaces_and_punctuation():
    parser = build_parser()
    args = parser.parse_args(["Hello World!"])

    assert args.text == "Hello World!"


def test_parse_args_accepts_multiline_text():
    parser = build_parser()
    text = "line one\nline two"
    args = parser.parse_args([text])

    assert args.text == text


def test_parse_args_missing_text_exits():
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_main_prints_stats_for_hello_world_with_exclamation(capsys):
    main(["Hello World!"])
    captured = capsys.readouterr()

    assert "Text: Hello World!" in captured.out
    assert "Word count: 2" in captured.out
    assert "Character count: 12" in captured.out


def test_main_prints_zero_word_count_for_empty_string(capsys):
    main([""])
    captured = capsys.readouterr()

    assert "Word count: 0" in captured.out
    assert "Is empty: True" in captured.out


def test_main_prints_zero_stats_for_whitespace_only(capsys):
    main(["     "])
    captured = capsys.readouterr()

    assert "Word count: 0" in captured.out
    assert "Character count: 0" in captured.out
    assert "Line count: 0" in captured.out
    assert "Is empty: True" in captured.out


def test_main_prints_line_count_for_multiline_text(capsys):
    main(["a\nb\nc"])
    captured = capsys.readouterr()

    assert "Line count: 3" in captured.out
    assert "Word count: 3" in captured.out


def test_main_character_count_without_spaces_is_less_when_spaces_present(capsys):
    main(["a b"])
    captured = capsys.readouterr()

    assert "Character count: 3" in captured.out
    assert "Character count without spaces: 2" in captured.out


def test_main_character_counts_match_for_single_word_without_spaces(capsys):
    main(["hello"])
    captured = capsys.readouterr()

    assert "Character count: 5" in captured.out
    assert "Character count without spaces: 5" in captured.out


def test_main_handles_unicode_text(capsys):
    main(["שלום עולם"])
    captured = capsys.readouterr()

    assert "Word count: 2" in captured.out
    assert "Is empty: False" in captured.out


def test_main_counts_hyphenated_phrase_as_two_words(capsys):
    main(["well-known release"])
    captured = capsys.readouterr()

    assert "Word count: 2" in captured.out


def test_main_prints_single_word_stats(capsys):
    main(["Python"])
    captured = capsys.readouterr()

    assert "Word count: 1" in captured.out
    assert "Line count: 1" in captured.out


def test_main_output_matches_analyze_text_for_sample(capsys):
    text = "Python is powerful"
    main([text])
    captured = capsys.readouterr()
    result = analyze_text(text)

    assert f"Word count: {result['word_count']}" in captured.out
    assert f"Line count: {result['line_count']}" in captured.out
    assert f"Is empty: {result['is_empty']}" in captured.out


def test_build_parser_description_is_set():
    parser = build_parser()

    assert parser.description == "Analyze text and return basic statistics."
