import random
import shutil

from tapi import app
from flask import jsonify, request

from config import *
from function import *


#
# Client SIP account method:
#
#
# метод необходим чтобы вывести информацию о клиентском SIP trunk по ид
#
# /tapi/v1.0/sip_account/<int:account_id>
# "status": str,  # ('REGED','UNREGED','BLOCKED')
@app.route('/tapi/v1.0/sip_account_2/<int:account_id>', methods=['GET'])
def get_sip_account_by_id(account_id):
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_sip_account_by_id.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | account_id: {}'.format(method_name, now(), unique_request_id, account_id))

    if not exist_sip_account_id(unique_request_id, account_id):
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
        sql_select_name_by_id = 'select name, is_blocked from ext_sip_accounts where id = {};'.format(account_id)

        print('{} | {} | {} | '
              'sql_select_name_by_id: {}'.format(method_name, now(), unique_request_id, sql_select_name_by_id))
        logging.info('{} | {} | {} | '
                     'sql_select_name_by_idt: {}'.format(method_name, now(), unique_request_id, sql_select_name_by_id))

        x.execute(sql_select_name_by_id)
        sql_select_result = x.fetchone()
        print('{} | {} | {} | sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))

        account_name = sql_select_result[0]
        is_blocked = sql_select_result[1]

        if is_blocked:
            status = 'BLOCKED'
        else:
            result_status_request = execute_esl_command_slowly('sofia status gateway {}'.format(account_name), esl_host)
            status = parse_esl_status_response(unique_request_id, result_status_request)

            if status != 'REGED':
                status = 'UNREGED'

        json_response = {
            "id": account_id,
            "status": status,
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
# метод необходим чтобы вывести информацию о сторонних SIP учетках по id:
#
@app.route('/tapi/v1.0/sip_account/<int:account_id>', methods=['GET'])
def get_ext_sip_account_by_id(account_id):
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_ext_sip_account_by_id.__name__

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    if not exist_sip_account_id(unique_request_id, account_id):
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
        sql_select_request_by_id = 'select  name, username, password, domain, proxy, port, expires, number, ' \
                                   'server, is_blocked, is_disabled from ext_sip_accounts where id = {};'.format(account_id)

        print('{} | {} | {} | '
              'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))
        logging.info('{} | {} | {} | '
                     'sql_select_request: {}'.format(method_name, now(), unique_request_id, sql_select_request_by_id))

        x.execute(sql_select_request_by_id)
        sql_select_result = x.fetchone()
        print('{} | {} | {} | sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        logging.info('{} | {} | {} | '
                     'sql_select_result: {}'.format(method_name, now(), unique_request_id, sql_select_result))
        print('0')

        name = sql_select_result[0]
        username = sql_select_result[1]
        password = sql_select_result[2]
        domain = sql_select_result[3]
        proxy = sql_select_result[4]
        port = sql_select_result[5]
        expires = sql_select_result[6]
        number = sql_select_result[7]
        server = sql_select_result[8]
        is_blocked = sql_select_result[9]
        is_disabled = sql_select_result[10]

        print('1')

        if is_blocked == '0':
            is_blocked = False
        elif is_blocked == '1':
            is_blocked = True
        elif is_blocked == 0:
            is_blocked = False
        elif is_blocked == 1:
            is_blocked = True

        if is_disabled == '0':
            is_disabled = False
        elif is_disabled == '1':
            is_disabled = True
        elif is_disabled == 0:
            is_disabled = False
        elif is_disabled == 1:
            is_disabled = True

        if is_blocked:
            state = 'BLOCKED'
        elif is_disabled:
            state = 'REGED'
        else:
            result_status_request = execute_esl_command_slowly('sofia status gateway ' + str(name), esl_host)
            state = parse_esl_status_response(unique_request_id, result_status_request)

        print('2')

        if state != 'BLOCKED' and state != 'REGED':
            state = 'UNREGED'

        json_response = {
            "id": account_id,
            "name": name,
            "status": state,
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
# метод для разблокировки SIP аккаунтов по дате
#
@app.route('/tapi/v1.0/sip_account/unblock', methods=['GET'])
def unblock_sip_account_by_date():
    unique_request_id = random.randint(1, 4294967296)
    method_name = get_ext_sip_account_by_id.__name__

    args = request.args
    date = args.get('date')

    print('{} | {} | {} | start'.format(method_name, now(), unique_request_id))
    logging.info('{} | {} | {} | start'.format(method_name, now(), unique_request_id))

    if not date or validate_date(unique_request_id, date):
        json_response = {
            "status_code": 12,
            "status_info": "bad param",
            "date": date,
            "date_format": "%Y-%m-%d"
        }

        print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
        logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

        return jsonify(json_response), 400

    unblock_sip_accounts_list = os.listdir(BLOCK_SIP_ACCOUNT_PATH + date)
    logging.info('{} | {} | {} | unblock_sip_accounts_list: {}'.format(method_name, now(), unique_request_id,
                                                                        unblock_sip_accounts_list))

    for sip_account in unblock_sip_accounts_list:
        unblocking_path = UNBLOCK_SIP_ACCOUNT_PATH + date + '/'
        try:
            logging.info('{} | {} | {} | sip_account: {}'.format(method_name, now(), unique_request_id,
                                                                                sip_account))

            logging.info('{} | {} | {} | copy: {} {}'.format(method_name, now(), unique_request_id,
                                                             BLOCK_SIP_ACCOUNT_PATH + date + '/' + sip_account,
                                                             XML_USER_FILE_PATH + sip_account))
            shutil.copy2(BLOCK_SIP_ACCOUNT_PATH + date + '/' + sip_account, XML_USER_FILE_PATH + sip_account)

            logging.info('{} | {} | {} | path: {}{}'.format(method_name, now(), unique_request_id,
                                                            unblocking_path, sip_account))

            check_path(unique_request_id, unblocking_path)

            logging.info('{} | {} | {} | move: {} {}'.format(method_name, now(), unique_request_id,
                                                             BLOCK_SIP_ACCOUNT_PATH + date + '/' + sip_account,
                                                             unblocking_path + sip_account))

            shutil.move(BLOCK_SIP_ACCOUNT_PATH + date + '/' + sip_account, unblocking_path + sip_account)

            unblock_sip_account(unique_request_id, sip_account[0:-4:])

        except IOError as e:
            print('{} | {} | {} | not found: {}'.format(method_name, now(), unique_request_id,
                                                        unblocking_path + sip_account))

    cmd = 'sofia profile external rescan'
    print('{} | {} | {} | esl cmd: {}'.format(method_name, now(), unique_request_id, cmd))
    logging.info('{} | {} | {} | esl cmd: {}'.format(method_name, now(), unique_request_id, cmd))
    execute_esl_command(cmd, esl_host)

    json_response = {
        "status_code": 1,
        "status_info": "successfully unblock"
    }

    print('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))
    logging.info('{} | {} | {} | json_response: {}'.format(method_name, now(), unique_request_id, json_response))

    return jsonify(json_response), 200
