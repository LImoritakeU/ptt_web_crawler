from datetime import datetime
from concurrent import futures

from google.cloud.storage import Blob
from ptt2json import init_session, PttPost

from src import logger, cli, bucket, subscriber


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

    max_workers = 20
    chunksize = 1000
    # with open("text.txt", "r") as f:
    #    urls = f.readlines()
    urls = [url.strip() for url in urls]
    urls_chunks = [urls[i : i + chunksize] for i in range(0, len(urls), chunksize)]

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for chunks in urls_chunks:
            session = init_session()
            results = executor.map(lambda url: consume_url(url, session), chunks)
            results = filter(lambda r: isinstance(r, str), results)
            s = "\n".join(results)
            insert_to_gcs(s)
