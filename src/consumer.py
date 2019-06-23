from concurrent import futures

from ptt2json import init_session, PttPost

from src import logger


def consume_url(url, session=None):
    if session is None:
        session = init_session()
    try:
        post: PttPost = PttPost(url, session)
        p = post.to_json()
        return p
    except Exception as e:
        logger.error("error: {} {}".format(url, e))


def consume_urls_parallel(urls):
    """consume url and transfer to multi-line json
    """

    ls = []
    max_workers = 20
    chunksize = 1000
    urls = [url.strip() for url in urls]
    urls_chunks = [urls[i : i + chunksize] for i in range(0, len(urls), chunksize)]

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for chunks in urls_chunks:
            session = init_session()
            results = executor.map(lambda url: consume_url(url, session), chunks)
            results = filter(lambda r: isinstance(r, str), results)
            s = "\n".join(results)
            ls.append(s)

    s = "\n".join(ls)
    return s
