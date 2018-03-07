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
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': d.send_msg_queue('MyQueue1', 'test')
    }
