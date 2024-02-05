import re
import random
import hashlib

from tapi import app
from flask import abort, jsonify, request

from config import *
from function import *


@app.route('/tapi/v1.0/originate', methods=['POST'])
def originate():
    if not request.json:
        return jsonify({'status': "nok"}), 400

    if not request.json or not 'caller_id' in request.json:
        abort(400)

    if not request.json or not 'did' in request.json:
        abort(400)

    if not request.json or not 'dial_timeout' in request.json:
        abort(400)

    if not request.json or not 'duration_limit' in request.json:
        abort(400)

    if not request.json or not 'call_id' in request.json:
        abort(400)

    if not request.json or not 'logic_id' in request.json:
        abort(400)

    if not request.json or not 'role' in request.json:
        abort(400)

    caller_id = request.json['caller_id']
    did = request.json['did']
    bnum = did
    anum = caller_id
    clid = request.json['clid']
    call_id = request.json['call_id']
    callback_id = request.json['callback_id']
    dial_timeout = request.json['dial_timeout']
    duration_limit = request.json['duration_limit']
    logic_id = request.json['logic_id']
    role = request.json['role']
    # is_premedia = request.json['is_premedia']
    is_premedia = False
    diversion_number = request.json['diversion_number']

    if not 'trunk_id' in request.json or request.json['trunk_id'] == "-1" or request.json['trunk_id'] == "0":
        trunk_id = None
    else:
        trunk_id = request.json['trunk_id']

    if not 'operator_trunk_id' in request.json or request.json['operator_trunk_id'] != 11:
        operator_trunk_id = None
    else:
        operator_trunk_id = request.json['operator_trunk_id']

    # origination_uuid = random.randint(1, 4294967296)
    m = hashlib.md5()
    m.update(now())
    mdate = m.hexdigest()
    origination_uuid = str(mdate) + "-" + str(random.randint(1, 4294967296))

    unique_id = random.randint(1, 4294967296)

    logging.info("lpt_callback | {} | {} | origination_uuid: {}".format(
        now(), str(unique_id), origination_uuid)
    )

    logging.info("lpt_callback | {} | {} | request_json: {}".format(
        now(), str(unique_id), request.data)
    )

    logging.info("lpt_callback | {} | {} | caller_id={} did={} clid={} call_id={} callback_id={}".format(
        now(), str(unique_id), caller_id, did, clid, call_id, callback_id)
    )
    logging.info("lpt_callback | {} | {} | dial_timeout={} duration_limit={} logic_id={} role={}".format(
        now(), str(unique_id), dial_timeout, duration_limit, logic_id, role)
    )
    logging.info("lpt_callback | {} | {} | trunk_id={}".format(
        now(), str(unique_id),  str(trunk_id))
    )
    logging.info("lpt_callback | {} | {} | operator_trunk_id={}".format(
        now(), str(unique_id),  str(operator_trunk_id))
    )
    logging.info("lpt_callback | {} | {} | is_premedia: {}".format(
        now(), str(unique_id),  str(is_premedia))
    )


    if trunk_id:
        if is_premedia:
            originate_cmd = 'originate {diversion_number=' + str(diversion_number) + ',is_premedia=' + str(is_premedia) + ',clid=' + str(clid) + ',operator_trunk_id=' + str(operator_trunk_id) + ',trunk_id=' + str(trunk_id) + ',logic_id=' + str(logic_id) + ',role=' + str(
                role) + ',originate_timeout=' + str(dial_timeout) + ',origination_uuid=' + str(
                origination_uuid) + ',origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
                unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
                dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/client_trunk_callback-leg-a_0' + str(
                bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'
        else:
            originate_cmd = 'originate {diversion_number=' + str(diversion_number) + ',is_premedia=' + str(is_premedia) + ',clid=' + str(clid) + ',operator_trunk_id=' + str(operator_trunk_id) + ',trunk_id=' + str(trunk_id) + ',logic_id=' + str(logic_id) + ',role=' + str(
                role) + ',originate_timeout=' + str(dial_timeout) + ',origination_uuid=' + str(
                origination_uuid) + ',ignore_early_media=true,origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
                unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
                dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/client_trunk_callback-leg-a_0' + str(
                bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'
    else:
        if is_premedia:
            originate_cmd = 'originate {diversion_number=' + str(diversion_number) + ',is_premedia=' + str(is_premedia) + ',clid=' + str(clid) + ',operator_trunk_id=' + str(operator_trunk_id) + ',logic_id=' + str(logic_id) + ',role=' + str(role) + ',originate_timeout=' + str(
                dial_timeout) + ',origination_uuid=' + str(
                origination_uuid) + ',origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
                unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
                dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/callback-leg-a_0' + str(
                bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'
        else:
            originate_cmd = 'originate {diversion_number=' + str(diversion_number) + ',is_premedia=' + str(is_premedia) + ',clid=' + str(clid) + ',operator_trunk_id=' + str(operator_trunk_id) + ',logic_id=' + str(logic_id) + ',role=' + str(role) + ',originate_timeout=' + str(
                dial_timeout) + ',origination_uuid=' + str(
                origination_uuid) + ',ignore_early_media=true,origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
                unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
                dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/callback-leg-a_0' + str(
                bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'

#    if trunk_id:
#        originate_cmd = 'originate {trunk_id=' + str(trunk_id) + ',logic_id=' + str(logic_id) + ',role=' + str(
#            role) + ',originate_timeout=' + str(dial_timeout) + ',origination_uuid=' + str(
#            origination_uuid) + ',origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
#            unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
#            dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/client_trunk_callback-leg-a_0' + str(
#            bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'
#    else:
#        originate_cmd = 'originate {logic_id=' + str(logic_id) + ',role=' + str(role) + ',originate_timeout=' + str(
#            dial_timeout) + ',origination_uuid=' + str(
#            origination_uuid) + ',origination_caller_id_number=' + str(anum) + ',unique_id=' + str(
#            unique_id) + ',callback_id=' + str(callback_id) + ',dial_timeout=' + str(
#            dial_timeout) + ',duration_limit=' + str(duration_limit) + '}loopback/callback-leg-a_0' + str(
#            bnum) + '/public callback-leg-b_' + str(bnum) + ' xml public'

    logging.info("lpt_callback | {} | {} | originate_cmd={}".format(
        now(), str(unique_id), originate_cmd)
    )

    node_ip = None
    flag_already_processed_that_clid = 0
    is_enabled_autofunnel_logic = True

    if clid:
        flag_already_processed_that_clid = check_exist_clid_in_key_member(clid)

        if flag_already_processed_that_clid == 1:
            node_ip = get_node_ip_from_pair_clid_node_ip(clid)
            if node_ip is None or node_ip == "None":
                pass
            else:
                is_enabled_autofunnel_logic = False
            logging.info("lpt_callback | {} | {} | get_node_ip_from_pair_clid_node_ip | that call for node_ip={}".format(
                now(), str(unique_id), node_ip)
            )
        else:
            node_ip = get_node_ip_from_clid(clid, nodes)
            if node_ip is None or node_ip == "None":
                pass
            else:
                is_enabled_autofunnel_logic = False
            logging.info("lpt_callback | {} | {} | get_node_ip_from_clid | that call for node_ip={}".format(
                now(), str(unique_id), node_ip)
            )

    if (node_ip is None or node_ip == "None") and call_id:
        node_ip = get_node_ip_from_call_id_redis(call_id, nodes)
        if node_ip is None or node_ip == "None":
            pass
        else:
            is_enabled_autofunnel_logic = False
        logging.info("lpt_callback | {} | {} | get_node_ip_from_call_id_redis | that call for node_ip={}".format(
            now(), str(unique_id), node_ip)
        )

        # balancer:
        if node_ip is None or node_ip == "None":
            esl_calls_count_string_node_1 = (execute_esl_command_slowly('show calls count', '31.131.249.26'))
            esl_calls_count_node_1 = int(esl_calls_count_string_node_1.split()[0])

            esl_calls_count_string_node_2 = (execute_esl_command_slowly('show calls count', '31.131.249.29'))
            esl_calls_count_node_2 = int(esl_calls_count_string_node_2.split()[0])

            logging.info("lpt_callback | {} | {} | esl_calls_count_node_1={}, esl_calls_count_node_2={}".format(
                now(), str(unique_id), esl_calls_count_node_1, esl_calls_count_node_2)
            )

            if esl_calls_count_node_1 == -1 and esl_calls_count_node_2 >= 0:
                # node_ip = redis_host_cl_2
                node_ip = nodes.get('fs-2')
                redis_ip = redis_host_cl_2

            elif esl_calls_count_node_2 == -1 and esl_calls_count_node_1 >= 0:
                # node_ip = redis_host_cl_1
                node_ip = nodes.get('fs-1')
                redis_ip = redis_host_cl_1

            elif esl_calls_count_node_1 >= 0 and esl_calls_count_node_1 <= esl_calls_count_node_2:
                # node_ip = redis_host_cl_1
                node_ip = nodes.get('fs-1')
                redis_ip = redis_host_cl_1

            elif esl_calls_count_node_2 >= 0 and esl_calls_count_node_2 <= esl_calls_count_node_1:
                # node_ip = redis_host_cl_2
                node_ip = nodes.get('fs-2')
                redis_ip = redis_host_cl_2

            if balancer_enable != 1:
                # node_ip = redis_host_cl_1
                node_ip = nodes.get('fs-1')
                redis_ip = redis_host_cl_1

            # if node_ip is None:
            #     node_ip = redis_host_cl_1

             # if node_ip is None:
            #     random_bit = random.getrandbits(1)
            #     if bool(random_bit):
            #         node_ip = redis_host_cl_2
            #     else:
            #         node_ip = redis_host_cl_1

            logging.info("lpt_callback | {} | {} | balancer | that call for node_ip={}".format(
                now(), str(unique_id), node_ip)
            )

    # if node_ip is None or node_ip == "None":
    #     node_ip = redis_host_cl_1

    if node_ip is None or node_ip == "None":
        random_bit = random.getrandbits(1)
        if bool(random_bit):
            # node_ip = redis_host_cl_2
            node_ip = nodes.get('fs-2')
            redis_ip = redis_host_cl_2

        else:
            # node_ip = redis_host_cl_1
            node_ip = nodes.get('fs-1')
            redis_ip = redis_host_cl_1

    call_case = clid.split('-')[1]
    logging.info("lpt_callback | {} | {} | call_case={}".format(
        now(), str(unique_id), call_case)
    )

    if re.search(r'autofunnel', call_case) and is_enabled_autofunnel_logic:
        logging.info("lpt_callback | {} | {} | that call is autofunnel".format(
            now(), str(unique_id))
        )
        # # node_ip = redis_host_cl_3
        # node_ip = nodes.get('fs-3')
        # redis_ip = redis_host_cl_3

#        random_bet = random.getrandbits(1)
#        if bool(random_bet):
#            node_ip = nodes.get('fs-4')
#            redis_ip = redis_host_cl_4
#
#        else:
#            node_ip = nodes.get('fs-3')
#            redis_ip = redis_host_cl_3

        node_name = random.choice(['fs-3', 'fs-4', 'fs-5'])
        if node_name == 'fs-3':
            node_ip = nodes.get('fs-3')
            redis_ip = redis_host_cl_3
        elif node_name == 'fs-4':
            node_ip = nodes.get('fs-4')
            redis_ip = redis_host_cl_4
        else:
            node_ip = nodes.get('fs-5')
            redis_ip = redis_host_cl_5

        call_count = {}
        for key, val in autofunnel_nodes.items():
            count = int(execute_redis_command('GET', "call_count:" + key, host=redis_host, port=redis_port, db=redis_db))
            call_count[key] = count

        k = min(call_count, key=call_count.get)
        node_ip = nodes.get(k)
        redis_ip = redis_hosts.get(k)

        logging.info("lpt_callback | {} | {} | k={} node_ip={} redis_ip={}".format(
            now(), str(unique_id), k, node_ip, redis_ip)
        )


#        node_ip = nodes.get('fs-5')
#        redis_ip = redis_host_cl_5

#        if bool(random_bet):
#            node_ip = nodes.get('fs-3')
#            redis_ip = redis_host_cl_3
#
#        else:
#            node_ip = nodes.get('fs-4')
#            redis_ip = redis_host_cl_4

    if flag_already_processed_that_clid == 0:
        execute_redis_command('SET', "pair_clid_node_ip-"+clid, node_ip, host=redis_host, port=redis_port, db=redis_db)
        execute_redis_command('SADD', "clid_key_member", clid, host=redis_host, port=redis_port, db=redis_db)

    execute_esl_command(originate_cmd, node_ip)

    logging.info("lpt_callback | {} | {} | originate sent cmd={}, node_ip={}".format(
        now(), str(unique_id), originate_cmd, node_ip)
    )

    return jsonify(
        {
            "status_code": "1",
            "status_info": "ok"
        }
    ), 200
