import logging
import json
from datetime import datetime
from google.cloud.storage import Client
from google.cloud import pubsub_v1
from google.cloud.storage.blob import Blob

status_filename = "status.json"


class CrawlerGCSConfig:
    def __init__(self, bucket, blob_path):
        self.bucket = bucket
        self.blob_path = blob_path
        self.blob = self.bucket.get_blob(self.blob_path)
        if not self.blob.exist():
            pass
        json.loads(self.blob.download_as_string())


class CrawlerGCSStatus:
    def __init__(self, bucket, blob_path):
        self.bucket = bucket
        self.blob_path = blob_path
        self.blob = Blob(blob_path, self.bucket)

        self.get()

    def get(self):
        try:
            self.content = json.loads(self.blob.download_as_string())
        except:
            raise ValueError

        return self.content

    def update(self, board, initial_timestamp, last_timestamp):
        self.content.setdefault(board, dict())
        self.content[board]["initial_timestamp_utc+8"] = initial_timestamp
        self.content[board]["last_timestamp_utc+8"] = last_timestamp
        self.blob.upload_from_string(json.dumps(self.content))


def update_status(data):
    if "attributes" in data:
        initial_timestamp = data["attributes"]["initial_timestamp"]
        last_timestamp = data["attributes"]["last_timestamp"]
        boardname = data["attributes"]["boardname"]

        status: dict = json.loads(read_from_gcs(status_filename))
        status.setdefault(boardname, dict())
        status[boardname]["initial_timestamp_utc+8"] = initial_timestamp
        status[boardname]["last_timestamp_utc+8"] = last_timestamp
        insert_to_gcs(folder="", content_str=json.dumps(status))


def read_from_gcs(path):
    blob = bucket.get_blob(path)
    return blob.download_as_string()


def insert_to_gcs(folder="", content_str=None):
    utcnow_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    blob = bucket.blob(f"{folder}/{utcnow_str}")
    blob.upload_from_string(content_str)


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    # fh = logging.FileHandler("ptt.log")
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


logger = setup_logger()

# cli: Client = Client.from_service_account_json()
cli: Client = Client()
bucket = cli.get_bucket("ptt_crawl_v2")


def setup_config():
    config = {
        "retry_limit": 3,
        "delay_days": 1,
        "project_id": "294873307860",
        "pubsub_topic": "ptt_urls",
        "subscriber_name": "ptt",
        "gcs_bucket": ""
    }

    return config


config = setup_config()
status = CrawlerGCSStatus(bucket, status_filename)

publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(config["project_id"], config["pubsub_topic"])
subscriber_name = "projects/{}/subscriptions/{}".format(
    config["project_id"], config["subscriber_name"]
)
try:
    subscriber.create_subscription(subscriber_name, topic_path)
except Exception as e:
    logger.warning(e)
