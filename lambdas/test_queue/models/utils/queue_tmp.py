#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# queues.py
# @Author : Gustavo M Freitas (gustavomf@ciandt.com)
# @Link   : https://github.com/gustavomf-cit
# @Date   : 3/7/2018, 12:04:04 PM

import boto3
import json


class QueueManager(object):

    _dict_topics = {}
    _queues = {}

    def __init__(self):
        self.client_sns = boto3.client(
            'sns',
            endpoint_url="http://localhost:4575",
            use_ssl=False,
            aws_access_key_id='ACCESS_KEY',
            aws_secret_access_key='SECRET_KEY',
            region_name='us-east-1')
        self.client_sqs = boto3.client(
            'sqs',
            endpoint_url="http://localhost:4576",
            use_ssl=False,
            aws_access_key_id='ACCESS_KEY',
            aws_secret_access_key='SECRET_KEY',
            region_name='us-east-1')
        self.queues = self.client_sqs.list_queues()
        for i in self.queues:
            print(i)

    def create_sns_topic(self, topic_name='notifications-injection'):
        """
        Get or create the SNS topic.
            :param self: itself
        """
        self.topic_name = topic_name
        # Creating a topic is idempotent, so if it already exists
        # then we will just get the topic returned.
        arn_value = self.client_sns.create_topic(Name=topic_name)['TopicArn']
        self._dict_topics[topic_name] = dict(arn=arn_value, queues=[])
        return arn_value

    def create_sqs_queue(self, topic_name, queue_name):
        """
        Create a new queue and assigne to a SNS topic
            :param self: itself
            :param topic_name: topic name
            :param queue_name: queue name
        """

        if topic_name not in self._dict_topics.keys():
            return False

        queue = self.client_sqs.create_queue(QueueName=queue_name)
        print(queue)
        queue_arn = queue['QueueUrl']
        print(queue_arn)

        if queue_arn not in self._dict_topics[topic_name]['queues']:
            self._dict_topics[topic_name]['queues'].append(queue_arn)
            self._queues[queue_name] = queue_arn

        subscribed = False
        topic = self.client_sns.Topic(self._dict_topics[topic_name]['arn'])
        for subscription in topic.subscriptions.all():
            if subscription.attributes['Endpoint'] == queue_arn:
                subscribed = True
                break

        if not subscribed:
            topic.subscribe(Protocol='sqs', Endpoint=queue_arn)

        return queue_arn

    def send_msg_queue(self, queue_name, message):
        """
        Create a new message to a queue that will trigger a
        lambda when received on topic
            :param self: itself
            :param queue_name: queue name
            :param message: message txt that you want to keep in queue
        """

        if queue_name not in self._queues.keys():
            return False

        queue = self.client_sqs.get_queue_by_name(QueueName=queue_name)

        response = queue.send_message(MessageBody=message)

        return response

    def send_msg_topic(self, topic_name, message):
        """
        Create a new message to a queue that will trigger a
        lambda when received on topic
            :param self: itself
            :param topic_name: topic name
            :param message: message txt that you want to keep in queue
        """

        if topic_name not in self._dict_topics.keys():
            return False

        response = self.client_sns.publish(
            TargetArn=self._dict_topics[topic_name]['arn'],
            Message=json.dumps({
                'default': json.dumps(message),
                'sms': 'here a short version of the message',
                'email': 'here a longer version of the message'
            }),
            Subject='a short subject for your message',
            MessageStructure='json')

        return response
