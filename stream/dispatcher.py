import json
import os
import random
import sys
import time
import uuid
from datetime import datetime, timezone

import pika

EXCHANGE = "rapido-dispatch"
ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "whitefield"],
}
TYPES = ["ride", "food"]
# Keep the broker URL out of Git: read it from an environment variable.
URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def make_message(city, zone, order_type):
    return {
        "id": uuid.uuid4().hex[:8],
        "city": city,
        "zone": zone,
        "type": order_type,
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def publish(channel, routing_key, message):
    channel.basic_publish(exchange=EXCHANGE, routing_key=routing_key, body=json.dumps(message))
    print(f"published key={routing_key} id={message['id']}", flush=True)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")

    # Optional: python dispatcher.py some.routing.key  -> publish that one key and exit
    if len(sys.argv) > 1:
        key = sys.argv[1]
        parts = key.split(".")
        zone = parts[1] if len(parts) > 1 else None
        order_type = parts[2] if len(parts) > 2 else None
        publish(channel, key, make_message(parts[0], zone, order_type))
        connection.close()
        return

    try:
        while True:
            city = random.choice(list(ZONES))
            zone = random.choice(ZONES[city])
            order_type = random.choice(TYPES)
            publish(channel, f"{city}.{zone}.{order_type}", make_message(city, zone, order_type))
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()


if __name__ == "__main__":
    main()