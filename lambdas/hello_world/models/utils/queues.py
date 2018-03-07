#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# queues.py
# @Author : Gustavo M Freitas (gustavomf@ciandt.com)
# @Link   : https://github.com/gustavomf-cit
# @Date   : 3/7/2018, 12:04:04 PM

import boto3


class QueueManager(object):

    _dict_topics = {}

    def __init__(self):
        self.client_sns = boto3.client('sns')
        self.client_sqs = boto3.client('sqs')

    def create_sns_topic(self, topic_name='notifications-injection'):
        """
        Get or create the SNS topic.
            :param self: itself
        """
        self.topic_name = topic_name
        # Creating a topic is idempotent, so if it already exists
        # then we will just get the topic returned.
        arn_value = self.client_sns.create_topic(Name=topic_name).arn
        self._dict_topics[topic_name] = dict(arn=arn_value, queues=[])
        return arn_value

    def create_sqs_queue(self, queue_name, topic_name):
        self._dict_topics[topic_name]

        queue = self.client_sqs.create_queue(QueueName=queue_name)
        self.queue_arn = queue.attributes['QueueArn']