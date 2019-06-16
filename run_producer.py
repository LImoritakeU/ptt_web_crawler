from datetime import datetime
import json
import urllib3

from src import config, publisher, topic_path
from src.producer import produce_urls


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if __name__ == "__main__":
    result = produce_urls()
    initial_timestamp = result["initial_timestamp"]
    last_timestamp = result["last_timestamp"]
    boardname = config["boardname"]

    publisher.publish(
        topic_path,
        json.dumps(result["urls"]).encode("utf-8"),
        initial_timestamp=str(initial_timestamp),
        last_timestamp=str(last_timestamp),
        boardname=boardname,
    )

    """

    with open(
        "urls_from_{}_to_{}.txt".format(initial_timestamp, last_timestamp), "w"
    ) as f:
        f.write(json.dumps(result))
    """

    with open("status.json", "r+") as f:
        obj = json.loads(f.read())
        obj["ptt"][boardname]["initial_timestamp_utc+8"] = initial_timestamp
        obj["ptt"][boardname]["last_timestamp_utc+8"] = last_timestamp

        f.seek(0)
        f.write(json.dumps(obj))
        f.truncate()
