import os
import json
import time
from pymongo import MongoClient
import pika


def main():
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    rabbitmq_user = os.environ.get("RABBITMQ_USER", "admin")
    rabbitmq_pass = os.environ.get("RABBITMQ_PASSWORD", "rabbitmq")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    status_collection = db["interface_status"]

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)

    connection = None
    for try_count in range(10):
        try:
            print(f"Connecting to RabbitMQ (try {try_count})...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials)
            )
            break
        except Exception as e:
            print(f"Failed: {e}")
            time.sleep(3)

    if not connection:
        print("Could not connect to RabbitMQ.")
        return

    channel = connection.channel()
    channel.exchange_declare(exchange="jobs", exchange_type="direct")
    channel.queue_declare(queue="router_jobs")
    channel.queue_bind(
        queue="router_jobs", exchange="jobs", routing_key="check_interfaces"
    )

    def callback(ch, method, properties, body):
        try:
            data = json.loads(body.decode("utf-8"))
            router_ip = data.get("ip") or data.get("hostname") or "unknown"
            print(f"Received job for router {router_ip}")

            # Mocked interface status response
            mock_interfaces = [
                {
                    "interface": "GigabitEthernet0/0",
                    "ip_address": router_ip,
                    "status": "up",
                    "proto": "up",
                },
                {
                    "interface": "GigabitEthernet0/1",
                    "ip_address": "unassigned",
                    "status": "administratively down",
                    "proto": "down",
                },
                {
                    "interface": "GigabitEthernet0/2",
                    "ip_address": "unassigned",
                    "status": "administratively down",
                    "proto": "down",
                },
                {
                    "interface": "GigabitEthernet0/3",
                    "ip_address": "unassigned",
                    "status": "administratively down",
                    "proto": "down",
                },
            ]

            print(json.dumps(mock_interfaces, indent=2))

            doc = {
                "router_ip": router_ip,
                "timestamp": time.strftime(
                    "%Y-%m-%dT%H:%M:%S.000+00:00", time.gmtime()
                ),
                "interfaces": mock_interfaces,
            }
            status_collection.insert_one(doc)
            print(f"Stored interface status for {router_ip}")

        except Exception as e:
            print(f"Error processing job: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="router_jobs", on_message_callback=callback)
    print("Worker is waiting for messages...")
    channel.start_consuming()


if __name__ == "__main__":
    main()
