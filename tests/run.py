import json

from src import logger, insert_to_gcs, publisher, topic_path, bucket, status
from src.consumer import consume_urls_parallel
from src.producer import produce_urls
from main import publisher_handler

publisher_handler("", "", "Gossiping")

# def subscriber_handler(data, context, board):
#     if "data" in data:
#         results_json = data["data"]
#         logger.warning("results data: {}".format(results_json))
#         # results_json = data["data"].decode("utf-8")
#         urls = json.loads(results_json)
#
#         s = consume_urls_parallel(urls)
#         insert_to_gcs(board, s)
#
#
# data = {}
# with open("pub") as f:
#     d = f.read()
#     data["data"] = d
# subscriber_handler(data, "", "gossiping")
