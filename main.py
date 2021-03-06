import os
import json
import base64

from src import status, publisher, topic_path, insert_to_gcs, logger, bucket
from src.consumer import consume_urls_parallel
from src.producer import produce_urls


def subscriber_handler(data, context, board):
    if "data" in data:
        results_json = base64.b64decode(data["data"]).decode("utf-8")
        logger.warning("results data: {}".format(results_json))
        # results_json = data["data"].decode("utf-8")
        urls = json.loads(results_json)

        s = consume_urls_parallel(urls)
        board = board.lower()
        insert_to_gcs(board, s)


def publisher_handler(data, context, board):
    result = produce_urls(board)
    initial_timestamp = result["initial_timestamp"]
    last_timestamp = result["last_timestamp"]
    urls = result["urls"]
    data = json.dumps(urls).encode("utf-8")

    publisher.publish(topic_path, data)
    blob = bucket.blob("pub/urls_from_{}_to_{}".format(initial_timestamp, last_timestamp))
    blob.upload_from_string(data.decode("utf-8"))
    status.update(board, initial_timestamp, last_timestamp)


def pipeline_handler(data, context):
    role = os.environ["role"]
    board = os.environ["board"]
    if role == "publisher":
        publisher_handler(data, context, board)
    elif role == "subscriber":
        subscriber_handler(data, context, board)

