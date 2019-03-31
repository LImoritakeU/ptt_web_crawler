import logging
from datetime import datetime
from concurrent import futures

from google.cloud.storage import Client
from google.cloud.storage import Blob

from ptt import init_session, PttPost

cli: Client = Client.from_service_account_json(
    "/home/shihhao/cloud_auth/firestore_la.json"
)
bucket = cli.get_bucket("ptt_crawl_v2")


def consume_url(url, session=None):
    if session is None:
        session = init_session()
    post: PttPost = PttPost(url, session)
    try:
        p = post.to_json()
        return p
    except Exception as e:
        logger.error("error: {} {}".format(post.url, e))

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)
    fh = logging.FileHandler("ptt.log")
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


logger = setup_logger()

def insert_to_gcs(content_str):
    utcnow_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    with open("./results/{}.txt".format(utcnow_str), 'w') as f:
        f.write(content_str)
    blob: Blob = bucket.blob(f"gossiping/{utcnow_str}")
    blob.upload_from_string(content_str)


def main():
    max_workers = 20
    with open("text.txt", 'r') as f:
        urls = f.readlines()

    urls = [url.strip() for url in urls]
    chunksize = 1000
    urls_chunks = [urls[i:i + chunksize] for i in range(0, len(urls), chunksize)]

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for chunks in urls_chunks:
            session = init_session()
            results = executor.map(lambda url: consume_url(url, session), chunks)

            results = filter(lambda r: isinstance(r, str), results)

            s = "\n".join(results)
            insert_to_gcs(s)


if __name__ == '__main__':
    main()
