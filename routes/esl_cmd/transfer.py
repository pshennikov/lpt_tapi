import random
import shutil

from tapi import app
from flask import abort, jsonify, request

from config import *
from function import *


# ################# UUID TRANSFER ##################

@app.route('/tapi/v1.0/transfer', methods=['POST'])
def uuid_transfer():
    ur_id = random.randint(1, 4294967296)
    method_name = uuid_transfer.__name__

    logging.info('{} | {} | {} | start'.format(method_name, now(), ur_id))

    if not request.json:
        logging.info("{} | {} | {} | the request doesn't have json header".format(method_name, now(), ur_id))
        return jsonify({'status': "nok"}), 400
    else:
        logging.info('{} | {} | {} | requset.json: {}'.format(method_name, now(), ur_id, request.data))

    if not request.json or not 'uuid' in request.json:
        logging.info("{} | {} | {} | abort request, because uuid wasn't set".format(method_name, now(), ur_id))
        abort(400)

    uuid = str(request.json['uuid'])
    logging.info("{} | {} | {} | uuid: {}".format(method_name, now(), ur_id, uuid))

    node_name = execute_redis_command('GET', "node_" + str(uuid), host=redis_host, port=redis_port, db=redis_db)

    # !!! Существует проблема в том что не всегда когда прилетает килл, имя ноды уже записано в основной редис!
    # Из-за этого в конце я отправляю команду на все ноды. НЕОБХОДИМО НАЙТИ РЕШЕНИЕ ЭТОЙ ПРОБЛЕМЫ
    # (как вариант записывать инфу о вызове на тапи в вмомент инициации вызова)!
    if not node_name or node_name not in nodes.keys():
        logging.info("{} | {} | {} | node_name: {}".format(method_name, now(), ur_id, node_name))
        logging.info("{} | {} | {} | try to use random node_name from nodes".format(method_name, now(), ur_id))
        node_name = random.choice(list(nodes.keys()))

    node_ip = nodes.get(node_name)
    node_redis_ip = redis_hosts.get(node_name)

    logging.info("{} | {} | {} | node_name: {}".format(method_name, now(), ur_id, node_name))
    logging.info("{} | {} | {} | node_ip: {}".format(method_name, now(), ur_id, node_ip))
    logging.info("{} | {} | {} | node_redis_ip: {}".format(method_name, now(), ur_id, node_redis_ip))

    use_child_lega_uuid = execute_redis_command('GET', 'use_child_lega_uuid_' + uuid, host=node_redis_ip, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | use_child_lega_uuid: {}".format(method_name, now(), ur_id, use_child_lega_uuid))

    if use_child_lega_uuid == '1':
        logging.info("{} | {} | {} | use_child_lega_uuid == '1', try to get child uuid".format(method_name, now(), ur_id))
        uuid = execute_redis_command('GET', 'child_lega_uuid_' + uuid, host=node_redis_ip, port=redis_port, db=redis_db)
        logging.info("{} | {} | {} | uuid: {}".format(method_name, now(), ur_id, uuid))

    execute_redis_command('SET', 'call_transfered_' + uuid, '0', host=node_redis_ip, port=redis_port, db=redis_db)

    logging.info("{} | {} | {} | redis set: leg_transferred_by_back/{} 1".format(method_name, now(), ur_id, uuid))
    execute_redis_command('SET', 'leg_transferred_by_back/' + uuid, '1', host=node_redis_ip, port=redis_port, db=redis_db)

    logging.info("{} | {} | {} | esl cmd: uuid_transfer {} proceed_after_transfer".format(method_name, now(), ur_id, uuid))

    cmd = 'uuid_transfer ' + uuid + ' proceed_after_transfer'
    execute_esl_command(cmd, node_ip)

    for key, value in nodes.items():
        if value != node_ip:
            execute_esl_command(cmd, value)

    logging.info("{} | {} | {} | sent esl cmd: {}".format(method_name, now(), ur_id, cmd))

    return jsonify(
        {
            "status_code": "1",
            "status_info": "ok"
        }
    ), 200
