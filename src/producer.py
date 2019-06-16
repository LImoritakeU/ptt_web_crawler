import time
import traceback
from datetime import datetime, timedelta

from ptt2json import PttPage

from src import logger, config

"""

皆為UTF-8 unix time

initial_timestamp: 首次爬取的時間戳記
last_timestamp: 最後回傳的最後一筆時間戳記
until_timestamp: 限定一天以前, 不爬取一天以內的文章
"""

board = config["boardname"]
retry_limit = config.get("retry_limit", 3)
initial_timestamp: int = config["status"]["ptt"][board]["initial_timestamp_utc+8"]
delay_days = config.get("delay_days", 1)


def produce_urls():
    result = {"urls": [], "initial_timestamp": initial_timestamp, "last_timestamp": ""}
    max_ts = 0
    retry_times = 0
    until = datetime.utcnow() - timedelta(days=delay_days) + timedelta(hours=8)  # UTC+8
    until_timestamp = until.timestamp()
    page: PttPage = PttPage(board)

    # Fist Time
    if page.is_last:
        page = page.get(page.number - 1)  # test and evaluate

    while True:
        try:
            posts = page.posts
            ts_list = [int(p["timestamp"]) for p in posts]

            if min(ts_list) < initial_timestamp:
                break

            if max(ts_list) > until_timestamp:
                pass

            else:
                posts = filter(
                    lambda post: int(post["timestamp"]) > initial_timestamp, posts
                )
                posts = filter(
                    lambda post: int(post["timestamp"]) < until_timestamp, posts
                )
                result["urls"].extend([post["url"] for post in posts])

                max_ts = max(ts_list) if max(ts_list) > max_ts else max_ts

            page = page.get_prev()
        except Exception as e:
            if retry_times <= retry_limit:
                retry_times += 1
                time.sleep(30)
            else:
                traceback.print(e)
                break

    result["last_timestamp"] = max_ts
    result["urls"].sort()

    logger.info("since: {}".format(initial_timestamp))
    logger.info("until: {}".format(max_ts))
    return result
