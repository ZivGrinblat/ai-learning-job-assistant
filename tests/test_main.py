import json

from app.main import format_analysis, parse_args, run


def test_run_returns_result_from_analyze_text():
    # Arrange
    text = "Hello world"

    # Act
    result = run(text)

    # Assert
    assert result == {
        "word_count": 2,
        "character_count": 11,
        "character_count_without_spaces": 10,
        "line_count": 1,
        "is_empty": False,
    }


def test_format_analysis_includes_all_stats():
    # Arrange
    text = "Hello world"
    analysis = run(text)

    # Act
    output = format_analysis(text, analysis)

    # Assert
    assert "Text: Hello world" in output
    assert "Words: 2" in output
    assert "Characters: 11" in output
    assert "Characters (no whitespace): 10" in output
    assert "Lines: 1" in output
    assert "Empty: False" in output


def test_parse_args_uses_text_from_command_line():
    # Act
    args = parse_args(["--text", "custom input"])

    # Assert
    assert args.text == "custom input"
    assert args.json is False


def test_main_json_flag_prints_analysis(capsys):
    # Arrange
    from app.main import main

    # Act
    main(["--text", "hi", "--json"])
    captured = capsys.readouterr()

    # Assert
    assert json.loads(captured.out) == run("hi")
