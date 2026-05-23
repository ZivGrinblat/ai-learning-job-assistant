from app.main import format_analysis, main, run


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


def test_main_prints_formatted_analysis(capsys):
    # Act
    main("Hello world")
    captured = capsys.readouterr()

    # Assert
    assert "Words: 2" in captured.out
    assert "Empty: False" in captured.out
