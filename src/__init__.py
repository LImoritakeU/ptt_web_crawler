import logging
import json

from google.cloud.storage import Client
from google.cloud import pubsub_v1


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
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


cli: Client = Client.from_service_account_json(
    "/home/shihhao/cloud_auth/firestore_la.json"
)
bucket = cli.get_bucket("ptt_crawl_v2")


def setup_config():
    # setup config
    with open("config.json") as f:
        config = json.loads(f.read())

    # setup status
    with open("status.json") as f:
        config["status"] = json.loads(f.read())

    return config


config = setup_config()
publisher = pubsub_v1.PublisherClient()
subscriber = pubsub_v1.SubscriberClient()
topic_path = publisher.topic_path(config["project_id"], config["pubsub_topic"])
subscriber_name = "projects/{}/subscriptions/{}".format(
    config["project_id"], config["subscriber_name"]
)
subscriber.create_subscription(subscriber_name, topic_path)
# cli: Client = Client.from_service_account_json(
#    "/home/shihhao/cloud_auth/spider.json"
# )
# bucket = cli.get_bucket("tw_forum_collect")
