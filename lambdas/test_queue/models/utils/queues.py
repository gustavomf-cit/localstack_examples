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
        self.load_clients()
        active_queues = self.client_sqs.list_queues()
        if 'QueueUrls' in active_queues:
            for iurl in active_queues['QueueUrls']:
                attr_queue = self.client_sqs.get_queue_attributes(
                    QueueUrl=iurl,
                    AttributeNames=['All'])['Attributes']['QueueArn']
                queue_name = attr_queue.split(":")[-1]
                self._queues[queue_name] = dict(url=iurl, arn=attr_queue)
        active_topics = self.client_sns.list_topics()
        if 'Topics' in active_topics:
            for topic_arn in active_topics['Topics']:
                topic_name = topic_arn['TopicArn'].split(":")[-1]
                self._dict_topics[topic_name] = dict(arn=topic_arn['TopicArn'])

    def list_queues(self):
        return self._queues

    def load_clients(self):
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

    def create_sns_topic(self, topic_name='notifications-injection'):
        """
        Get or create the SNS topic.
            :param self: itself
        """
        self.topic_name = topic_name
        # Creating a topic is idempotent, so if it already exists
        # then we will just get the topic returned.
        arn_value = self.client_sns.create_topic(Name=topic_name)['TopicArn']
        self._dict_topics[topic_name] = dict(arn=arn_value)
        return dict(topic=arn_value), 200

    def create_sqs_queue(self, queue_name):
        """
        Create a new queue and assigne to a SNS topic
            :param self: itself
            :param queue_name: queue name
        """

        queue = self.client_sqs.create_queue(QueueName=queue_name)
        queue_url = queue['QueueUrl']
        attr_queue = self.client_sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All'])['Attributes']['QueueArn']
        self._queues[queue_name] = dict(url=queue_url, arn=attr_queue)

        return dict(queue_url=queue_url), 200

    def send_msg_queue(self, queue_name, message):
        """
        Create a new message to a queue that will trigger a
        lambda when received on topic
            :param self: itself
            :param queue_name: queue name
            :param message: message txt that you want to keep in queue
        """

        response = self.client_sqs.send_message(
            QueueUrl=self._queues[queue_name], MessageBody=message)

        return dict(response=response), 200

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
            TopicArn=self._dict_topics[topic_name]['arn'],
            Message=json.dumps(message),
            Subject='SalesForce message',
            MessageStructure='json')

        return dict(response=response), 200

    def check_exists_subscription(self, topic_name, service_name,
                                  service_type):
        """
        check if a service to topic exists and do not duplicate it
            :param self: itself
            :param topic_name: topic name
            :param service_name: name or arn, depends of service_type option
            :param service_type: default is sqs, however there are other
            options => sqs|lambda|http|https|application|sms|email
        """
        list_subscriptions = self.client_sns.list_subscriptions_by_topic(
            TopicArn=self._dict_topics[topic_name]['arn'])
        if 'Subscriptions' not in list_subscriptions:
            return False

        for i in list_subscriptions['Subscriptions']:
            if ((i['Protocol'] == service_type) and
                (((service_type == 'sqs') and
                  (i['Endpoint'] == self._queues[service_name]['url'])) or
                 (i['Endpoint'] == service_name))):
                return True

        return False

    def set_topic_service(self, topic_name, service_name, service_type='sqs'):
        """
        Set a service to topic for trigger a service/queue/...
            :param self: itself
            :param topic_name: topic name
            :param service_name: name or arn, depends of service_type option
            :param service_type: default is sqs, however there are other
            options => sqs|lambda|http|https|application|sms|email
        """
        resp = self.check_exists_subscription(topic_name, service_name,
                                              service_type)
        if resp is True:
            return dict(message='Already exists'), 422
        if service_type == 'sqs':
            subscribe = self.client_sns.subscribe(
                TopicArn=self._dict_topics[topic_name]['arn'],
                Protocol='sqs',
                Endpoint=self._queues[service_name]['url'])['SubscriptionArn']
        elif service_type == 'lambda':
            subscribe = self.client_sns.subscribe(
                TopicArn=self._dict_topics[topic_name]['arn'],
                Protocol='lambda',
                Endpoint=service_name)['SubscriptionArn']
        else:
            return dict(message='Invalid service'), 422

        return dict(subscribe=subscribe), 200

    def get_message_queue(self, queue_name):
        """
        Get first message from queue
        VisibilityTimeout default is 10 seconds, that is mean
        if the message not been deleted in 30 seconds,
        it will go back to queue, to be process by another lambda
            :param self: itself
            :param queue_name: queue name
        """
        response = self.client_sqs.receive_message(
            QueueUrl=self._queues[queue_name]['url'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=30,
            WaitTimeSeconds=1)
        if 'Messages' not in response:
            return dict(message='No messages in the queue'), 422
        return dict(message=response['Messages']), 200

    def delete_msg_queue(self, message_id, receipt_handle):
        """
        delete a message in the SQS queue
            :param self: itself
            :param message_id: message id/arn
            :param receipt_handle: receipt_handle from message
        """
        response = self.client_sqs.delete_messages(Entries=[
            {
                'Id': message_id,
                'ReceiptHandle': receipt_handle
            },
        ])
        return dict(message=response), 200
