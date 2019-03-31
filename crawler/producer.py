from datetime import datetime, timedelta
from ptt import PttPage
from google.cloud.storage import Client
from google.cloud.storage import Blob
from google.cloud import pubsub_v1

project_id = ""
topic_name = ""

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)


cli: Client = Client.from_service_account_json(
    "/home/shihhao/cloud_auth/firestore_la.json"
)
bucket = cli.get_bucket("tw_forum_collect")



def get_ptt_page(board, number=None):
    return PttPage(board, number)


def setup_config():
    pass


def produce(url):



def insert_to_gcs(page, path):
    utcnow_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    blob: Blob = bucket.blob(f"ptt/gossiping/{utcnow_str}_{page}")
    with open(path, "rb") as f:
        blob.upload_from_file(f)

    return None


def produce_urls():
    website = 'ptt'
    board = 'Gossiping'
    until = datetime.utcnow() - timedelta(days=1) + timedelta(hours=8)
    until_timestamp = until.timestamp()
    last_timestamp: int = 1541466688
    page: PttPage = get_ptt_page(board)

    # Fist Time
    if page.is_last:
        page = page.get(page.number - 100)  # test and evaluate

    max_ts = 0


    while True:
        posts = page.posts
        ts_list = [int(p['timestamp']) for p in posts]

        if (min(ts_list) < last_timestamp):
            return

        if (max(ts_list) > until_timestamp):
            pass

        else:
            posts = filter(lambda post: int(post['timestamp']) > last_timestamp, posts)
            posts = filter(lambda post: int(post['timestamp']) < until_timestamp, posts)

            # [produce(post['url']) for post in posts]
            with open('text.txt', 'a') as f:
                [f.write(post['url'] + "\n") for post in posts]


            max_ts = max(ts_list)

        page = page.get_prev()

    last_timestamp = max_ts


