from ptt import PttPage

def test_over18():
    board = "Gossiping"
    page = PttPage.get_page(board)
    if page.url == "https://www.ptt.cc/ask/over18?from=%2Fbbs%2FGossiping%2Findex.html":
        assert False
    assert True
