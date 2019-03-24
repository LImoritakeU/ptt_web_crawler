from ptt import PttPage


board = "Gossiping"


def test_ptt_page_url():
    p: PttPage = PttPage.get_page(board)
    assert p.is_last is True


def test_page_last_page():
    p: PttPage = PttPage.get_page(board)
    assert p.is_last
    p.get(1)
    assert not p.is_last

