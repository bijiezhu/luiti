# -*- coding: utf-8 -*-

import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
os.environ['LUIGI_CONFIG_PATH'] = root_dir + '/tests/client.cfg'

import mock
import unittest

from luiti.tests import date_begin
from etl_utils import cached_property


class TestLuitiUtils(unittest.TestCase):

    @mock.patch("os.system")
    def test_MongoImportTask(self, os_system, ):
        os_system.return_value = 0

        from luiti import MongoImportTask

        class AnotherMongoDay(MongoImportTask):
            root_dir = "/tmp"

            mongodb_connection_address = ('192.168.20.111', 37001)
            database_name = "17zuoye_crm"
            collection_name = "teacher_report"
            tmp_filepath = "/foobar.json"
            data_file_collection_model = "MongoCollection(foobar)"

            is_collection_exists = lambda self: True

        mongo_task = AnotherMongoDay(date_value=date_begin)

        self.assertEqual(mongo_task.mongodb_connection_host, "192.168.20.111")
        self.assertEqual(mongo_task.mongodb_connection_port, 37001)
        self.assertEqual(mongo_task.mongoimport_command, "/usr/bin/mongoimport --host 192.168.20.111 --port 37001 --db 17zuoye_crm --collection teacher_report --file /foobar.json")
        self.assertEqual(mongo_task.tmp_dir, "/tmp/AnotherMongoDay")

        self.assertFalse(mongo_task.run())

    def test_StaticFile(self):
        from luiti import StaticFile, luigi

        class FoobarFileDay(StaticFile):
            data_file = "/foobar"
            IODevice = luigi.LocalTarget
        self.assertEqual(FoobarFileDay().output().path, "/foobar")

        class OldFoobarFileDay(StaticFile):
            filepath = "/foobar"
            IODevice = luigi.LocalTarget
        self.assertEqual(OldFoobarFileDay().output().path, "/foobar")
        self.assertTrue(OldFoobarFileDay().complete())
        self.assertFalse(OldFoobarFileDay().run())

    def test_TaskDate(self):
        from luiti.task_templates import TaskMonth, TaskDay

        class AnotherMonthDay(TaskMonth):
            root_dir = "/tmp"

        class AnotherDay(TaskDay):
            root_dir = "/tmp"

        m1 = AnotherMonthDay(date_value=date_begin)
        self.assertEqual(len(m1.days_in_month), 30)

        m2 = AnotherDay(date_value="2015-07-20")
        self.assertEqual(m2.latest_30_days[0].format('YYYY-MM-DD'), '2015-06-21')
        self.assertEqual(m2.latest_30_days[-1].format('YYYY-MM-DD'), '2015-07-20')
        self.assertEquals(len(m2.latest_30_days), 30)

        m3 = AnotherDay(date_value="2015-07-20")
        self.assertEquals(m3.latest_7_days[0].format('YYYY-MM-DD'), '2015-07-14')
        self.assertEqual(m3.latest_7_days[-1].format('YYYY-MM-DD'), '2015-07-20')
        self.assertEquals(len(m3.latest_7_days), 7)

    def test_HiveTask(self):
        from luiti.task_templates import HiveTask

        class AnotherHiveDay(HiveTask):
            run_mode = "local"  # dont print when run unit test
            root_dir = "/another/hive/result/"
            use_hive_db = "main_hive_database"

            @cached_property
            def sql_main(self):
                return "select * from example_table where dt=%s;" % self.date_str

        h1 = AnotherHiveDay(date_value=date_begin)
        self.assertEqual(h1.sql_main, "select * from example_table where dt=2014-09-01;")
        self.assertEqual(h1.query(), "USE main_hive_database; INSERT OVERWRITE DIRECTORY \"/another/hive/result/2014-09-01/another_hive_day.json\" select * from example_table where dt=2014-09-01;")

        class CompatibilityHiveDay(HiveTask):
            """ test old API """
            data_root = "/foobar"
            hive_db = "foobar"

        h2 = CompatibilityHiveDay(date_value=date_begin)
        self.assertEqual(h2.root_dir, "/foobar")
        self.assertEqual(h2.use_hive_db, "foobar")

    def test_requires_with_prev_week(self):
        from luiti.task_templates import TaskDay, TaskWeek

        class OneDay(TaskDay):
            root_dir = "/tmp"

        class AnotherWeek(TaskWeek):
            root_dir = "/tmp"

        w1 = AnotherWeek(date_value=date_begin)
        tasks = w1.requires_with_prev_week(OneDay)
        self.assertEqual(len(tasks), 8)


if __name__ == '__main__':
    unittest.main()
