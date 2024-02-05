import random
import shutil

from tapi import app
from flask import abort, jsonify, request

from config import *
from function import *


# ################# UUID BRIDGE ##################

@app.route('/tapi/v1.0/bridge', methods=['POST'])
def uuid_bridge():
    # ur_id - unique_request_id
    ur_id = random.randint(1, 4294967296)
    method_name = uuid_bridge.__name__

    logging.info('{} | {} | {} | start'.format(method_name, now(), ur_id))

    if not request.json:
        logging.info("{} | {} | {} | the request doesn't have json header".format(method_name, now(), ur_id))
        return jsonify({'status': "nok"}), 400
    else:
        logging.info('{} | {} | {} | requset.json: {}'.format(method_name, now(), ur_id, request.data))


    if not request.json or not 'uuida' in request.json:
        logging.info("{} | {} | {} | abort request, because uuida wasn't set".format(method_name, now(), ur_id))
        abort(400)

    if not request.json or not 'uuidb' in request.json:
        logging.info("{} | {} | {} | abort request, because uuidb wasn't set".format(method_name, now(), ur_id))
        abort(400)

    uuid1 = str(request.json['uuida'])
    uuid2 = str(request.json['uuidb'])

    logging.info("{} | {} | {} | uuid1: {}".format(method_name, now(), ur_id, uuid1))
    logging.info("{} | {} | {} | uuid2: {}".format(method_name, now(), ur_id, uuid2))

    node_name = execute_redis_command('GET', "node_" + str(uuid1), host=redis_host, port=redis_port, db=redis_db)
    node_ip = nodes.get(node_name)
    node_redis_ip = redis_hosts.get(node_name)

    logging.info("{} | {} | {} | node_name: {}".format(method_name, now(), ur_id, node_name))
    logging.info("{} | {} | {} | node_ip: {}".format(method_name, now(), ur_id, node_ip))
    logging.info("{} | {} | {} | node_redis_ip: {}".format(method_name, now(), ur_id, node_redis_ip))

    # leonid
    if node_ip is None or node_ip == "None":
        node_name ='fs-1'
        node_ip = nodes.get('fs-1')
        node_redis_ip = redis_host_cl_1

        logging.info("{} | {} | {} | node_name: {}".format(method_name, now(), ur_id, node_name))
        logging.info("{} | {} | {} | node_ip: {}".format(method_name, now(), ur_id, node_ip))
        logging.info("{} | {} | {} | node_redis_ip: {}".format(method_name, now(), ur_id, node_redis_ip))

##################
    # для чего эта переменная?
    execute_redis_command('SET', 'bridge_' + uuid1, uuid2, host=node_redis_ip, port=redis_port, db=redis_db)

    # следующими двумя переменными мы проверяем были ли мы уже сбриджены с другими уидами,
    # дальше по этим переменным мы примем решение нужно нам склеивать вызовы или нет.
    uuid2_bridged_flag_record = execute_redis_command('GET', "bridged_flag_record-" + uuid1, host=node_redis_ip,
                                                      port=redis_port, db=redis_db)
    uuid1_bridged_flag_record = execute_redis_command('GET', "bridged_flag_record-" + uuid2, host=node_redis_ip,
                                                      port=redis_port, db=redis_db)

    logging.info(" {} | {} | {} | uuid1_bridged_flag_record: {}".format(method_name, now(),
                                                                        ur_id, uuid1_bridged_flag_record))
    logging.info(" {} | {} | {} | uuid2_bridged_flag_record: {}".format(method_name, now(),
                                                                        ur_id, uuid2_bridged_flag_record))

    if uuid2_bridged_flag_record is not None and uuid2_bridged_flag_record != str(uuid2):
        execute_redis_command('SET', 'flag_stick_together_record-' + uuid1, '1', host=node_redis_ip, port=redis_port,
                              db=redis_db)
        logging.info(" {} | {} | {} | flag_stick_together_record-{} = 1".format(method_name, now(), ur_id, uuid1))

    if uuid1_bridged_flag_record is not None and uuid1_bridged_flag_record != str(uuid1):
        execute_redis_command('SET', 'flag_stick_together_record-' + uuid2, '1', host=node_redis_ip, port=redis_port,
                              db=redis_db)
        logging.info(" {} | {} | {} | flag_stick_together_record-{} = 1".format(method_name, now(), ur_id, uuid2))

################

    execute_redis_command('SET', "bridged_flag_record-"+uuid1, uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
    execute_redis_command('SET', "bridged_flag_record-"+uuid2, uuid1, host=node_redis_ip, port=redis_port, db=redis_db)

################

    call_type = execute_redis_command('GET', 'call_type_' + str(uuid1), host=redis_host, port=redis_port, db=redis_db)
    call_type_legb = execute_redis_command('GET', 'call_type_' + str(uuid2), host=redis_host, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | call_type: {}".format(method_name, now(), ur_id, call_type))
    logging.info("{} | {} | {} | call_type_legb: {}".format(method_name, now(), ur_id, call_type_legb))

    use_child_lega_uuid1 = execute_redis_command('GET', 'use_child_lega_uuid_' + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
    use_child_lega_uuid2 = execute_redis_command('GET', 'use_child_lega_uuid_' + uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | use_child_lega_uuid1: {}".format(method_name, now(), ur_id, use_child_lega_uuid1))
    logging.info("{} | {} | {} | use_child_lega_uuid2: {}".format(method_name, now(), ur_id, use_child_lega_uuid2))

    if use_child_lega_uuid1 == '1' and use_child_lega_uuid2 == '1':
        uuid1 = execute_redis_command('GET', 'child_lega_uuid_' + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
        uuid2 = execute_redis_command('GET', 'child_lega_uuid_' + uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
    elif use_child_lega_uuid1 == '1' and call_type_legb == 'callback':
        uuid1 = execute_redis_command('GET', 'child_lega_uuid_' + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
        uuid2 = execute_redis_command('GET', 'callback_second_id_' + uuid2, host=redis_host, port=redis_port, db=redis_db)
    elif use_child_lega_uuid2 == '1':
        uuid2 = execute_redis_command('GET', 'child_lega_uuid_' + uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
    else:
        if call_type == 'callback':
            uuid2 = execute_redis_command('GET', 'callback_second_id_' + uuid2, host=redis_host, port=redis_port, db=redis_db)
        elif call_type == 'in_call':
            uuid2 = execute_redis_command('GET', 'callback_second_id_' + uuid2, host=redis_host, port=redis_port, db=redis_db)
        elif call_type == 'call_transfer':
            uuid1 = execute_redis_command('GET', 'callback_second_id_' + uuid1, host=redis_host, port=redis_port, db=redis_db)
        elif call_type == 'call_release':
            uuid1 = execute_redis_command('GET', 'callback_second_id_' + uuid1, host=redis_host, port=redis_port, db=redis_db)

    logging.info("{} | {} | {} | esl cmd: uuid_bridge {} {}".format(method_name, now(), ur_id, uuid1, uuid2))

    # !!! Проверяем не зарелижены ли плечи вызова которые мы будем бриджить!
    call_hanguped_1 = execute_redis_command('GET', 'call_hanguped' + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
    call_hanguped_2 = execute_redis_command('GET', 'call_hanguped' + uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | call_hanguped_1: {}".format(method_name, now(), ur_id, call_hanguped_1))
    logging.info("{} | {} | {} | call_hanguped_2: {}".format(method_name, now(), ur_id, call_hanguped_2))

    if call_hanguped_1 == '1':
        esl_cmd = 'uuid_transfer'
        cmd = 'uuid_transfer ' + uuid2 + ' proceed_after_transfer'
    elif call_hanguped_2 == '1':
        esl_cmd = 'uuid_transfer'
        cmd = 'uuid_transfer ' + uuid1 + ' proceed_after_transfer'
    else:
        esl_cmd = 'uuid_bridge'
        cmd = 'uuid_bridge ' + uuid1 + ' ' + uuid2
        esl_uuid1 = uuid1
        esl_uuid2 = uuid2

    # !!! Проверяем не был ли плечо а затрансферено!
    call_transfered = execute_redis_command('GET', 'call_transfered_' + uuid1, host=redis_host, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | call_transfered: {}".format(method_name, now(), ur_id, call_transfered))

    # ??? Не совсем понтяно, что тут проверяем так как зарелижен или нет вызов проверили выше!
    end_callback_sended = execute_redis_command('GET', 'end_callback_sended-' + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
    logging.info("{} | {} | {} | end_callback_sended: {}".format(method_name, now(), ur_id, end_callback_sended))

    if call_transfered == '1' and end_callback_sended == '1':
        logging.info("{} | {} | {} | call_transfered=='1' & end_callback_sended=='1'".format(method_name, now(), ur_id))
        uuid_bridged = execute_redis_command('GET', "bridged_with-" + uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
        logging.info("{} | {} | {} | uuid_bridged: {}".format(method_name, now(), ur_id, uuid_bridged))
        esl_cmd = 'uuid_bridge'
        cmd = 'uuid_bridge ' + uuid_bridged + ' ' + uuid2
        esl_uuid1 = uuid_bridged
        esl_uuid2 = uuid2
    elif call_transfered != '1' and end_callback_sended == '1':
        logging.info("{} | {} | {} | call_transfered!='1' & end_callback_sended=='1'".format(method_name, now(), ur_id))
        esl_cmd = 'uuid_transfer'
        cmd = 'uuid_transfer ' + uuid2 + ' proceed_after_transfer'

    execute_esl_command(cmd, node_ip)

    for key, value in nodes.items():
        if value != node_ip:
            execute_esl_command(cmd, value)

    logging.info("{} | {} | {} | sent esl cmd: {}".format(method_name, now(), ur_id, cmd))

    if esl_cmd == 'uuid_bridge':
        execute_redis_command('SET', "bridged_with-" + esl_uuid1, esl_uuid2, host=node_redis_ip, port=redis_port, db=redis_db)
        execute_redis_command('SET', "bridged_with-" + esl_uuid2, esl_uuid1, host=node_redis_ip, port=redis_port, db=redis_db)
        execute_redis_command('SET', "bridged-" + esl_uuid1, '1', host=node_redis_ip, port=redis_port, db=redis_db)
        execute_redis_command('SET', "bridged-" + esl_uuid2, '1', host=node_redis_ip, port=redis_port, db=redis_db)

    return jsonify(
        {
            "status_code": "1",
            "status_info": "ok"
        }
    ), 200
