import os
import json

from google.cloud.storage.blob import Blob

from src import read_from_gcs, insert_to_gcs, bucket, status, publisher, topic_path
from src.consumer import consume_urls_parallel
from src.producer import produce_urls


def subscriber_handler(data, context, board):

    if "data" in data:
        results_json = data["data"].decode("utf-8")
        results = json.loads(results_json)
        print(results)


def publisher_handler(data, context, board):
    result = produce_urls(board)
    initial_timestamp = result["initial_timestamp"]
    last_timestamp = result["last_timestamp"]

    publisher.publish(topic_path, json.dumps(result["urls"]).encode("utf-8"))
    status.update(board, initial_timestamp, last_timestamp)


def pipeline_handler(data, context):
    role = os.environ["role"]
    board = os.environ["board"]

    if role == "publisher":
        publisher_handler(data, context, board)
    elif role == "subscriber":
        subscriber_handler(data, context, board)


if __name__ == "__main__":
    publisher_handler("", "", "Gossiping")
