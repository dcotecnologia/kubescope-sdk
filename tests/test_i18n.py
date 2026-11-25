from kubescope.sdk import set_translator, translate


def test_a_text_comes_back_as_it_is_until_the_app_gives_a_translator() -> None:
    set_translator(None)
    assert translate("Page", "Instances") == "Instances"


def test_the_translator_of_the_app_is_asked_for_the_context_and_the_text() -> None:
    set_translator(lambda context, text: f"{context}:{text.upper()}")
    try:
        assert translate("Page", "Instances") == "Page:INSTANCES"
    finally:
        set_translator(None)
