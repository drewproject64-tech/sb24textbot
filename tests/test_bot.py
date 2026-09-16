from bot import MAX_TEXT_LENGTH, build_dispatcher, count_text, main_menu, rearrange_text, sort_words


def test_sort_words():
    assert sort_words("banana apple Orange") == "apple banana Orange"


def test_count_text():
    assert count_text("Hello world!\nSB24") == (3, 17, 14, 2)


def test_rearrange_text_single_character():
    assert rearrange_text("a") == "a"


def test_rearrange_text_returns_text():
    result = rearrange_text("hello")
    assert sorted(result) == sorted("hello")


def test_text_length_limit_constant():
    assert MAX_TEXT_LENGTH == 4000


def test_dispatcher_builds():
    dispatcher = build_dispatcher()
    assert dispatcher is not None


def test_main_menu_has_three_core_tools():
    keyboard_text = [
        button.text
        for row in main_menu().inline_keyboard
        for button in row
    ]
    assert keyboard_text[:3] == ["🔤 Sort Words", "🔢 Count Text", "🔀 Rearrange Text"]
    assert "💡 Examples" not in keyboard_text
