import os
import json

from src import status, publisher, topic_path, insert_to_gcs
from src.consumer import consume_urls_parallel
from src.producer import produce_urls


def subscriber_handler(data, context, board):
    if "data" in data:
        results_json = data["data"].decode("utf-8")
        results = json.loads(results_json)
        urls = results["urls"]

        s = consume_urls_parallel(urls)
        insert_to_gcs(board, s)


def publisher_handler(data, context, board):
    result = produce_urls(board)
    initial_timestamp = result["initial_timestamp"]
    last_timestamp = result["last_timestamp"]
    urls = result["urls"]

    publisher.publish(topic_path, json.dumps(urls).encode("utf-8"))
    status.update(board, initial_timestamp, last_timestamp)


def pipeline_handler(data, context):
    role = os.environ["role"]
    board = os.environ["board"]
    if role == "publisher":
        publisher_handler(data, context, board)
    elif role == "subscriber":
        subscriber_handler(data, context, board)

