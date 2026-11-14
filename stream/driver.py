import json
import os
import sys

import pika

EXCHANGE = "rapido-dispatch"
URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")


def main():
    if len(sys.argv) != 3:
        print("usage: python driver.py NAME PATTERN")
        sys.exit(1)
    name, pattern = sys.argv[1], sys.argv[2]

    connection = pika.BlockingConnection(pika.URLParameters(URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")

    # Private queue: the broker picks the name, and it is deleted when this driver disconnects.
    queue = channel.queue_declare(queue="", exclusive=True).method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue, routing_key=pattern)
    print(f"[{name}] waiting with pattern '{pattern}' on queue {queue}", flush=True)

    def on_message(ch, method, properties, body):
        message = json.loads(body)
        if "zone" not in message:
            print(f"[{name}] REJECTED key={method.routing_key} id={message.get('id')} (zone missing)", flush=True)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)   # discard it, do not retry
        else:
            print(f"[{name}] key={method.routing_key} id={message.get('id')} "
                  f"zone={message.get('zone')} type={message.get('type')}", flush=True)
            ch.basic_ack(delivery_tag=method.delivery_tag)                   # processed OK

    channel.basic_consume(queue=queue, on_message_callback=on_message)  # manual ACK (auto_ack=False)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()


if __name__ == "__main__":
    main()