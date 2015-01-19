#-*-coding:utf-8-*-

from ..parameter import ArrowParameter
import luigi
from datetime import datetime

class Files(object):

    @staticmethod
    def get_all_date_file_to_task_instances(date_range, task_classes):
        """ return all instances in date range. """
        assert len(date_range) == 17, "[error] correct format is \"20140901-20140905\", but the input is %s" % date_range
        first_date, last_date = date_range[0:8], date_range[9:]
        first_date, last_date = ArrowParameter.get(first_date, "YYYYMMDD"), ArrowParameter.get(last_date, "YYYYMMDD")

        return dict({ file_3 : task_instance_2 \
                    for task1 in task_classes \
                    for task_instance_2 in task1.instances_by_date_range(first_date, last_date) \
                    for file_3 in task_instance_2._persist_files + [task_instance_2.data_file]})

    @staticmethod
    def soft_delete_files(*files):
        delete_at_str = datetime.now().strftime("-deleted-at-%Y%m%d-%H%M%S")

        for file1 in sorted(files):
            print "[delete file]", file1
            if luigi.hdfs.client.exists(file1):
                luigi.hdfs.client.rename(file1, file1 + delete_at_str)
                print
            else:
                print "[err] doesnt exist!"

        print "\nDone!"
        return 0
