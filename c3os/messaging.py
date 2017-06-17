import pika

from c3os import conf


CONF = conf.CONF
rpc_host = CONF['rpc']['address']
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=rpc_host))
channel = connection.channel()

channel.queue_declare(queue=CONF['os_info']['REGION_NAME'])


def publish(body):
    """ Publishing message.

    Args:
        body (str): message.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rpc_host))
    channel = connection.channel()

    channel.basic_publish(exchange='',
                          routing_key=CONF['os_info']['REGION_NAME'],
                          body=body)
