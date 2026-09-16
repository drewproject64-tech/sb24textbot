from bot import MAX_TEXT_LENGTH, NEWS, build_dispatcher, count_text, main_menu, sort_words


def test_sort_words():
    assert sort_words("banana apple Orange") == "apple banana Orange"


def test_count_text():
    assert count_text("Hello world!\nSB24") == (3, 17, 15, 2)


def test_news_exists_without_external_destination():
    assert len(NEWS) >= 3
    for title, body in NEWS:
        assert title
        assert body
        assert "http://" not in body
        assert "https://" not in body
        assert "t.me/" not in body


def test_text_length_limit_constant():
    assert MAX_TEXT_LENGTH == 4000


def test_dispatcher_builds():
    assert build_dispatcher() is not None


def test_main_menu_has_exactly_three_core_functions():
    buttons = [
        button.text
        for row in main_menu().inline_keyboard
        for button in row
    ]
    assert buttons[:3] == ["🔤 Sort Words", "🔢 Count Text", "📰 News & Updates"]
    assert "🔀 Rearrange Text" not in buttons
