import random

from tapi import app
from flask import jsonify, request

from config import *
from function import *

#
# Client SIP Trunk method:
#
# метод необходим чтобы вывести информацию о всех клиентских SIP trunk созданных в системе
#
@app.route('/tapi/v1.0/client_trunk', methods=['GET'])
def get_client_trunk():
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_client_trunk.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_select_request = 'select id,proxy,port,username,password,flag_auth,client_id from client_trunk;'
        print("{} | {} | {} | sql_select_request: {}".format(method_name, now(), unique_request_id, sql_select_request))
        logging.info('{} | {} | {} | '
                     'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request))

        x.execute(sql_select_request)
        sql_select_result = x.fetchmany(SELECT_LIMIT)

        print("{} | {} | {} | sql_select_result: {}".format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))

        json_response = []
        for s in sql_select_result:
            print("{} | {} | {} | {}".format(method_name, now(), unique_request_id, s))
            logging.info('{} | {} | {} | {}'.format(method_name, now(), unique_request_id, s))

            trunk_id = s[0]
            proxy = s[1]
            port = s[2]
            username = s[3]
            password = s[4]
            flag_auth = s[5]
            client_id = s[6]

            sip_trunk = {
                "trunk_id": trunk_id,
                "host": proxy,
                "port": port,
                "username": username,
                "password": password,
                "auth": flag_auth,
                "client_id": client_id
            }
            json_response.append(sip_trunk)

        conn.commit()

    except:
        print("{} | {} | {} | can't connect to make select request".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | can't connect to make select req.".format(method_name, now(), unique_request_id))

        conn.rollback()
        conn.close()
        json_response = {
                "status_code": 0,
                "status_info": "request failed"
        }

        print("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))
        logging.info("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 500

    conn.close()
    print("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))
    logging.info("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200


#
# метод необходим чтобы вывести информацию о клиентском SIP trunk по ид
#
@app.route('/tapi/v1.0/client_trunk/<int:trunk_id>', methods=['GET'])
def get_client_trunk_by_id(trunk_id):
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_client_trunk_by_id.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    if not exist_trunk_id(unique_request_id, trunk_id):
        json_response = {
            "status_code": 11,
            "status_info": "not found"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_select_request_by_id = 'select proxy, port, username, password, flag_auth, client_id from client_trunk ' \
                             'where id = {};'.format(trunk_id)

        print('{} | {} | {} | '
              'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))
        logging.info('{} | {} | {} | '
                     'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))

        x.execute(sql_select_request_by_id)
        sql_select_result = x.fetchone()
        print('{} | {} | {} | sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))

        proxy = sql_select_result[0]
        port = sql_select_result[1]
        username = sql_select_result[2]
        password = sql_select_result[3]
        flag_auth = sql_select_result[4]
        if flag_auth == 0:
            flag_auth = False
        elif flag_auth == 1:
            flag_auth = True

        client_id = sql_select_result[5]

        result_status_request = execute_esl_command_slowly('sofia status gateway ' + CUSTOM_TRUNK_PREFIX + str(trunk_id), redis_host)
        # state = 'REGED'
        state = parse_esl_status_response(unique_request_id, result_status_request)

        if state == 'Parsing_Error':
            state = 'UNREGED'

        json_response = {
            "trunk_id": trunk_id,
            "host": proxy,
            "port": port,
            "username": username,
            "password": password,
            "auth": flag_auth,
            "client_id": client_id,
            "state": state,
        }

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
# Метод используется баскендом для создание нового клиентского SIP trunk:
#
@app.route('/tapi/v1.0/client_trunk', methods=['POST'])
def add_client_trunk():
    unique_request_id = random.randint(1, 4294967296)
    method_name = add_client_trunk.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

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

    # !!! надо дописать исключения!

    proxy = request.json['host']

    if 'port' not in request.json:
        port = 5060
    elif request.json['port'] == 0:
        port = 5060
    else:
        port = request.json['port']

    if not request.json['host'] or request.json['host'] == False:
        flag_auth = False
        username = None
        password = None
    else:
        flag_auth = request.json['flag_auth']
        username = request.json['username']
        password = request.json['password']

    if 'client_id' not in request.json:
        client_id = None
    else:
        client_id = request.json['client_id']

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        if not client_id:
            sql_insert_request = "insert into client_trunk (proxy,port,username,password,flag_auth) values " \
                             "('{}',{},'{}','{}',{})".format(proxy, port, username, password, flag_auth)
        else:
            sql_insert_request = "insert into client_trunk (proxy,port,username,password,flag_auth,client_id) values " \
                             "('{}',{},'{}','{}',{},{})".format(proxy, port, username, password, flag_auth, client_id)

        print('{} | {} | {} | sql_insert_request: {}'.format(method_name, now(), unique_request_id, sql_insert_request))
        logging.info('{} | {} | {} | '
                     'sql_insert_request: {}'.format(method_name, now(), unique_request_id, sql_insert_request))

        x.execute(sql_insert_request)

        # !!! Необходимо переделать бд сделать уникальным большее количество параметров, как следствие изменить селект!
        sql_select_request_id = "select id from client_trunk where proxy = '{}' and port = {} and username = '{}' " \
                                "and password = '{}'".format(proxy, port, username, password)

        print('{} | {} | {} | '
              'sql_select_request_id: {}'.format(method_name, now(), unique_request_id, sql_select_request_id))
        logging.info('{} | {} | {} | '
                     'sql_select_request_id: {}'.format(method_name, now(), unique_request_id, sql_select_request_id))

        x.execute(sql_select_request_id)

        trunk_id = x.fetchone()[0]

        print('{} | {} | {} | trunk_id: {}'.format(method_name, now(), unique_request_id, trunk_id))
        logging.info('{} | {} | {} | trunk_id: {}'.format(method_name, now(), unique_request_id, trunk_id))

        # # !!! Необходимо добавить нормальные переменные адресов, вместо использования переменных редиса (redis_host)!
        # execute_redis_command('SADD', 'custom_sip_trunk_id', trunk_id, host=redis_host, port=redis_port, db=redis_db)
        # custom_sip_trunk_id = execute_redis_command('SMEMBERS', 'custom_sip_trunk_id',
        #                                             host=redis_host, port=redis_port, db=redis_db)
        #
        # print('{} | {} | {} | custom_sip_trunk_id: {}, type: {}'.
        #       format(method_name, now(), unique_request_id, custom_sip_trunk_id, type(custom_sip_trunk_id)))
        # logging.info('{} | {} | {} | custom_sip_trunk_id: {}, type: {}'.
        #              format(method_name, now(), unique_request_id, custom_sip_trunk_id, type(custom_sip_trunk_id)))

        conn.commit()

        # Дальше блок кода взаимодействия с Freeswitch:
        # - создание XML файла
        # - запрос в ESL на перечитывание новых транков
        create_xml_file_for_custom_sip_user_trunk(proxy, port, username, password, XML_CUSTOM_TRUNK_FILE_PATH,
                                                  CUSTOM_TRUNK_PREFIX + str(trunk_id))
        # execute_esl_command('sofia profile external_client_trunk rescan ' + CUSTOM_TRUNK_PREFIX + str(trunk_id), redis_host)
        execute_esl_command('sofia profile external_client_trunk rescan', esl_host)

    except:
        print("{} | {} | {} | can't connect to make insert request".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | "
                     "can't connect to make insert request".format(method_name, now(), unique_request_id))

        conn.rollback()
        conn.close()
        json_response = {
                "status_code": 0,
                "status_info": "request failed"
            }

        print("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))
        logging.info("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 500

    conn.close()
    json_response = {
            "trunk_id": trunk_id,
            "status_code": "1",
            "status_info": "ok"
        }

    print("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))
    logging.info("{} | {} | {} | json_response: {}".format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200

#
# Метод используется баскендом для изменения параметров клиентского SIP trunk:
#
@app.route('/tapi/v1.0/client_trunk', methods=['PUT'])
def upd_client_trunk():
    unique_request_id = random.randint(1, 4294967296)
    method_name = upd_client_trunk.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    if not request.json:
        json_response = {
            "status_code": 10,
            "status_info": "bad id"
        }
        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_resp: {}'.format(method_name, now(), unique_request_id, json_response))
        return jsonify(json_response), 400
    else:
        print('{} | {} | {} | request.json: {}'.format(method_name, now(), unique_request_id, request.data))
        logging.info('{} | {} | {} | req.json: {}'.format(method_name, now(), unique_request_id, request.data))

    if 'trunk_id' not in request.json:
        json_response = {
            "status_code": 10,
            "status_info": "bad id"
        }
        print('{} | {} | {} | bad id'.format(method_name, now(), unique_request_id))
        logging.info('{} | {} | {} | bad id'.format(method_name, now(), unique_request_id))
        return jsonify(json_response), 400

    # !!! надо дописать исключения!

    trunk_id = request.json['trunk_id']

    if not exist_trunk_id(unique_request_id, trunk_id):
        json_response = {
            "status_code": 11,
            "status_info": "not found"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400

    proxy = request.json['host']

    if 'port' not in request.json:
        port = 5060
    elif request.json['port'] == 0:
        port = 5060
    else:
        port = request.json['port']

    username = request.json['username']
    password = request.json['password']
    flag_auth = request.json['flag_auth']

#    client_id = request.json['client_id']
    if 'client_id' not in request.json:
        client_id = None
    else:
        client_id = request.json['client_id']

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        if not client_id:
            sql_update_request = "update client_trunk set " \
                                 "proxy = '{}', " \
                                 "port = {}, " \
                                 "username = '{}', " \
                                 "password = '{}', " \
                                 "flag_auth = {} " \
                                 "where id = {};".format(proxy, port, username, password, flag_auth, trunk_id)

        else:
            sql_update_request = "update client_trunk set " \
                                 "proxy = '{}', " \
                                 "port = {}, " \
                                 "username = '{}', " \
                                 "password = '{}', " \
                                 "flag_auth = {}, " \
                                 "client_id = {} " \
                                 "where id ={};".format(proxy, port, username, password, flag_auth, client_id, trunk_id)

        print('{} | {} | {} | sql_insert_request: {}'.format(method_name, now(), unique_request_id, sql_update_request))
        logging.info('{} | {} | {} | '
                     'sql_insert_request: {}'.format(method_name, now(), unique_request_id, sql_update_request))

        x.execute(sql_update_request)
        conn.commit()

        # Дальше блок кода взаимодействия с Freeswitch:
        # - удаление XML файла
        # - запрос в ESL на удаления транка из БД Freeswitch
        delete_xml_file(XML_CUSTOM_TRUNK_FILE_PATH, CUSTOM_TRUNK_PREFIX + str(trunk_id), unique_request_id)
        execute_esl_command('sofia profile external_client_trunk killgw ' + CUSTOM_TRUNK_PREFIX + str(trunk_id), esl_host)

        # - создание XML файла
        # - запрос в ESL на перечитывание новых транков
        create_xml_file_for_custom_sip_user_trunk(proxy, port, username, password, XML_CUSTOM_TRUNK_FILE_PATH,
                                                  CUSTOM_TRUNK_PREFIX + str(trunk_id))
        execute_esl_command('sofia profile external_client_trunk rescan', esl_host)

    except:
        print("{} | {} | {} | can't connect to make update request".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | can't connect to make update req.".format(method_name, now(), unique_request_id))

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
    json_response = {
            "status_code": "1",
            "status_info": "ok"
        }

    print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
    logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200


# Метод необходим для удаления клиентского SIP trunk:
@app.route('/tapi/v1.0/client_trunk', methods=['DELETE'])
def del_client_trunk():
    unique_request_id = random.randint(1, 4294967296)
    method_name = del_client_trunk.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    if not request.json:
        json_response = {
            "status_code": 0,
            "status_info": "bad id"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400
    else:
        print('{} | {} | {} | request.json: {}'.format(method_name, now(), unique_request_id, request.data))
        logging.info('{} | {} | {} | req.json: {}'.format(method_name, now(), unique_request_id, request.data))

    logging.info('{} | {} | {} | 1'.format(method_name, now(), unique_request_id))

    if 'trunk_id' not in request.json:
        json_response = {
            "status_code": 0,
            "status_info": "bad id"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400

    trunk_id = request.json['trunk_id']

    logging.info('{} | {} | {} | before exist_trunk_id'.format(method_name, now(), unique_request_id))

    if not exist_trunk_id(unique_request_id, trunk_id):
        json_response = {
            "status_code": 11,
            "status_info": "not found"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400

    conn = MySQLdb.connect(host=db_host, port=db_port, user=db_user, passwd=db_password, db=db_database, charset='utf8')
    x = conn.cursor()
    try:
        sql_delete_request = 'delete from client_trunk ' \
                             'where id = {};'.format(trunk_id)

        print('{} | {} | {} | sql_delete_request: {}'.format(method_name, now(), unique_request_id, sql_delete_request))
        logging.info('{} | {} | {} | '
                     'sql_delete_request: {}'.format(method_name, now(), unique_request_id, sql_delete_request))

        x.execute(sql_delete_request)
        conn.commit()

        # Дальше блок кода взаимодействия с Freeswitch:
        # - удаление XML файла
        # - запрос в ESL на удаления транка из БД Freeswitch
        delete_xml_file(XML_CUSTOM_TRUNK_FILE_PATH, CUSTOM_TRUNK_PREFIX + str(trunk_id), unique_request_id)
        execute_esl_command('sofia profile external_client_trunk killgw ' + CUSTOM_TRUNK_PREFIX + str(trunk_id), esl_host)

    except:
        print("{} | {} | {} | can't connect to make delete request".format(method_name, now(), unique_request_id))
        logging.info("{} | {} | {} | can't connect to make delete req.".format(method_name, now(), unique_request_id))

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
    json_response = {
            "status_code": "1",
            "status_info": "ok"
    }

    print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
    logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200
