from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'broker:29092'})
