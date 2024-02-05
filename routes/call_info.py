import random

from tapi import app
from flask import jsonify, request

from config import *
from function import *


#
# get call info | now it return operator list who serves call
#
# метод возвращает список операторов обслуживающих вызов:
@app.route('/tapi/v1.0/call_info/<string:call_id>', methods=['GET'])
def get_call_info_by_call_id(call_id):
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_call_info_by_call_id.__name__

    conn = MySQLdb.connect(host=db_host_main, port=db_port, user=db_user_main, passwd=db_password_main, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_select_request_by_id = "select in_caller_id,out_caller_id,diversion,exten,in_calldate,out_calldate,clid," \
                                   "uuid,status,sip_cause_code,cause_code,operator,agent_leg,attempt_counter " \
                                   "from calls where clid = '{}';".format(call_id)

        print('{} | {} | {} | '
              'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))
        logging.info('{} | {} | {} | '
                     'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))

        x.execute(sql_select_request_by_id)
        sql_select_result = x.fetchall()
        print('{} | {} | {} | sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))

        calls = []
        for call in sql_select_result:
            json_call = {
                "in_caller_id": call[0],
                "out_caller_id": call[1],
                "diversion": call[2],
                "exten": call[3],
                "in_calldate": call[4],
                "out_calldate": call[5],
                "clid": call[6],
                "uuid": call[7],
                "status": call[8],
                "sip_cause_code": call[9],
                "cause_code": call[10],
                "operator": call[11],
                "agent_leg": call[12],
                "attempt_counter": call[13]
            }

            calls.append(json_call)

        json_response = {
            "call_id": call_id,
            "calls": calls,
        }

        print('json_response:', json_response)

        conn.commit()

    except:
        print("{} | {} | {} | can't connect to make select request by id".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | can't connect to "
                     "make select request by id".format(method_name, now(), unique_request_id))

        conn.rollback()
        conn.close()
        json_response = {
                "status_code": 0,
                "status_info": "request failed"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 500

    conn.close()

    print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
    logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200


#
# get call info | now it return operator list who serves call
#
# метод возвращает список операторов обслуживающих вызов:
@app.route('/tapi/v1.0/call_info_status', methods=['POST'])
def get_call_info_by_call_id_status():
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_call_info_by_call_id_status.__name__

    if not request.json:
        json_response = {
            "status_code": 12,
            "status_info": "bad param"
        }

        print('{} | {} | {} | json_responce: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_resp: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400
    else:
        print('{} | {} | {} | request.json: {}'.format(method_name, now(), unique_request_id, request.data))
        logging.info('{} | {} | {} | req.json: {}'.format(method_name, now(), unique_request_id, request.data))

    call_id = request.json['call_id']
    status = request.json['status']

    conn = MySQLdb.connect(host=db_host_main, port=db_port, user=db_user_main, passwd=db_password_main, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_select_request_by_id = "select in_caller_id,out_caller_id,diversion,exten,in_calldate,out_calldate,clid," \
                                   "uuid,status,sip_cause_code,cause_code,operator,agent_leg,attempt_counter " \
                                   "from calls where clid = '{}' and status = '{}';".format(call_id, status)

        print('{} | {} | {} | '
              'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))
        logging.info('{} | {} | {} | '
                     'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))

        x.execute(sql_select_request_by_id)
        sql_select_result = x.fetchall()
        print('{} | {} | {} | sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))

        calls = []
        for call in sql_select_result:
            json_call = {
                "in_caller_id": call[0],
                "out_caller_id": call[1],
                "diversion": call[2],
                "exten": call[3],
                "in_calldate": call[4],
                "out_calldate": call[5],
                "clid": call[6],
                "uuid": call[7],
                "status": call[8],
                "sip_cause_code": call[9],
                "cause_code": call[10],
                "operator": call[11],
                "agent_leg": call[12],
                "attempt_counter": call[13]
            }

            calls.append(json_call)

        json_response = {
            "call_id": call_id,
            "calls": calls,
        }

        print('json_response:', json_response)

        conn.commit()

    except:
        print("{} | {} | {} | can't connect to make select request by id".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | can't connect to "
                     "make select request by id".format(method_name, now(), unique_request_id))

        conn.rollback()
        conn.close()
        json_response = {
                "status_code": 0,
                "status_info": "request failed"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 500

    conn.close()

    print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
    logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200
