import pika
import json
from uuid import UUID

from c3os.cntl import utils as CU
from c3os import utils
from c3os import db
from c3os import conf
from c3os.objects.instance import Instance
from c3os.cntl.type import CNTLTYPE

db_pool = db.generate_pool()
nova = utils.connection_nova()
CONF = conf.CONF


def start():
    """ Start cntl server. """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=CONF['rpc']['address']))
    channel = connection.channel()

    channel.queue_declare(queue=CONF['os_info']['REGION_NAME'])

    channel.basic_consume(handle,
                          queue=CONF['os_info']['REGION_NAME'],
                          no_ack=True)

    channel.start_consuming()


def handle(ch, method, properties, body):
    """ Messeage handler. """
    data = json.loads(body.decode('utf-8'))

    if data['type'] == CNTLTYPE.CREATE_INSTANCE:
        create_instance(data['body'])
    elif data['type'] == CNTLTYPE.DELETE_INSTANCE:
        delete_instance(data['body'])


def create_instance(data):
    """ Create instance and regiser with DB. """
    db_pool.lock()
    ins = CU.create_instance(nova, data['name'] + '-migrate-test-from-c3os',
                             'ubuntu-16.04', 'm1.small', 'internal', 'k0ma')

    id = utils.generate_id(ins.id, conf.OWN_REGION_UUID)
    all_addresses = utils.conver_addresses(ins)
    instance = Instance(id, ins.status, all_addresses, **data)
    print('create instance:', instance.name)
    utils.write_log('create instance:' + instance.name)
    db_pool.add(instance)
    db_pool.commit()
    db_pool.unlock()


def delete_instance(data):
    """ Delete instance and regiser with DB. """
    db_pool.lock()
    instance = db_pool.search(Instance, data['colum'], data['value'])
    utils.write_log('delete' + instance.name)

    db_pool.delete(Instance, 'id', instance.id)
    nova.servers.delete(str(UUID(instance.os_uuid)))
    print('delete', instance.name)
    db_pool.commit()
