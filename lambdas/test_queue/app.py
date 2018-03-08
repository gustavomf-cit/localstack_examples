#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# lambda_queue.py.py
# @Author : Gustavo M Freitas (gustavomf@ciandt.com)
# @Link   : https://github.com/gustavomf-cit
# @Date   : 3/1/2018, 12:43:02 PM

import json
import boto3
from models.utils.queues import QueueManager


def lambda_handler(event, context):
    """
    lambda handler serverless
        :param event: lambda events (parameters from apigateway)
        :param context: lambda aws functions
    """

    d = QueueManager()
    resp = d.get_message_queue('x')

    message = json.dumps(resp[0])
    print("ok")
    print(message)
    print("ok")
    with open('../messages.sqs', 'a+') as filedump:
        filedump.write(message)
    return {
        'statusCode': resp[1],
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': message
    }
