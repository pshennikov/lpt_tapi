#!flask/bin/python
# coding=utf-8


import logging

from config import *
from function import *

from flask import Flask, jsonify, make_response


logging.basicConfig(filename=log_path, level=logging.INFO)

app = Flask(__name__)

# routes:
import routes.call_info
import routes.sip_account
import routes.sip_trunk

import routes.esl_cmd.originate
import routes.esl_cmd.local
import routes.esl_cmd.bridge
import routes.esl_cmd.kill
import routes.esl_cmd.transfer


# Блок обработки общих негативных кейсов:
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(host=redis_host, port="80", debug=True)
