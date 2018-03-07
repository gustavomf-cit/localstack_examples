#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# queue.py
# @Author : Gustavo M Freitas (gustavomf@ciandt.com)
# @Link   : https://github.com/gustavomf-cit
# @Date   : 3/7/2018, 10:51:57 AM

import pytds
import json


class Database(object):
    def test(self):
        with pytds.connect(
                dsn='xxxxxxxxxxxx',
                user='xxxxxxxxxxxxxxx',
                password='xxxxxxxxxxxxxxxxx',
                port=1433,
                database="xxxxxxxxxxxxxxxxxxx") as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select xxxxxx from xxxxx.dbo.xxxxxxxx;")
                rows = cur.fetchall()
                return json.dumps(rows)
