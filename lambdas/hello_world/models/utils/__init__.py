import logging
import logstash
import os
import json


class DummyLog(object):
    '''
    Dummy log class for aws lambda
    '''
    extra = {"project": "localstack", "lambda_name": "hello_world"}

    def __init__(self):
        logstash_addr = os.environ['LOGSTASH_SERVER']
        env_name = os.environ['ENV_LAMBDA']

        self.extra['enviroment'] = env_name

        logstash_addr = logstash_addr.format(env_name=env_name)
        logstash_port = 5045
        logger_logstash = logging.getLogger('localstack_examples')
        logger_logstash.handlers = []
        logger_logstash.setLevel(logging.INFO)
        logger_logstash.addHandler(
            logstash.TCPLogstashHandler(
                logstash_addr, logstash_port, version=1))

        self.logger_logstash = logger_logstash

    def info(self, message):
        self.logger_logstash.info(
            json.dumps({
                "msg": str(message),
                "logger_name": "localstack_examples"
            }),
            extra=self.extra)

    def warning(self, message):
        self.logger_logstash.warning(
            json.dumps({
                "msg": str(message),
                "logger_name": "localstack_examples"
            }),
            extra=self.extra)

    def error(self, message):
        self.logger_logstash.error(
            json.dumps({
                "msg": str(message),
                "logger_name": "localstack_examples"
            }),
            extra=self.extra)

    def debug(self, message):
        self.logger_logstash.debug(
            json.dumps({
                "msg": str(message),
                "logger_name": "localstack_examples"
            }),
            extra=self.extra)


logger = DummyLog()
