"""Instructor-written CLI checks derived from the published course contract."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

PROJECT=Path(os.environ['COURSE_SUBMISSION_DIR'])


class CLIAcceptance(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-B','orders_cli.py',*args],cwd=PROJECT,capture_output=True,text=True,timeout=10)

    def assert_result(self,args,expected):
        run=self.invoke(*args)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(run.stderr,'')
        self.assertEqual(json.loads(run.stdout),expected)

    def assert_service_error(self,args,message):
        run=self.invoke(*args)
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stdout,'')
        self.assertEqual(run.stderr.strip(),'error: '+message)

    def test_owner_and_status_both_required(self):
        self.assert_result(['--user','2','--status','shipped'],[{'id':11,'item':'mouse'}])

    def test_no_status_preserves_ana_source_order(self):
        self.assert_result(['--user','1'],[{'id':10,'item':'keyboard'},{'id':12,'item':'monitor'}])

    def test_empty_result_is_a_json_list(self):
        self.assert_result(['--user','2','--status','pending'],[])

    def test_unknown_user(self):
        self.assert_service_error(['--user','99'],'unknown user')

    def test_unknown_status(self):
        self.assert_service_error(['--user','2','--status','lost'],'unknown status')

    def test_service_validation_order_is_preserved(self):
        self.assert_service_error(['--user','99','--status','lost'],'unknown user')

    def test_missing_user_is_an_argument_error(self):
        run=self.invoke()
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stdout,'')
        self.assertIn('--user',run.stderr)

    def test_user_requires_an_integer(self):
        run=self.invoke('--user','Ben')
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stdout,'')
        self.assertIn('--user',run.stderr)

    def test_unknown_option_is_an_argument_error(self):
        run=self.invoke('--user','2','--invented-option')
        self.assertEqual(run.returncode,2)
        self.assertEqual(run.stdout,'')

    def test_help_does_not_run_the_order_query(self):
        run=self.invoke('--help')
        self.assertEqual(run.returncode,0)
        self.assertIn('--user',run.stdout)
        self.assertIn('--status',run.stdout)
        self.assertEqual(run.stderr,'')

    def test_import_is_quiet_and_does_not_parse_arguments(self):
        run=subprocess.run([sys.executable,'-B','-c','import orders_cli'],cwd=PROJECT,capture_output=True,text=True,timeout=10)
        self.assertEqual((run.returncode,run.stdout,run.stderr),(0,'',''))

    def test_main_accepts_an_argument_list_and_returns_zero(self):
        code="import orders_cli; raise SystemExit(orders_cli.main(['--user','2','--status','shipped']))"
        run=subprocess.run([sys.executable,'-B','-c',code],cwd=PROJECT,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout),[{'id':11,'item':'mouse'}])

    def test_main_does_not_mutate_shared_fixture(self):
        code="import copy,order_service,orders_cli; before=copy.deepcopy(order_service.ORDERS); orders_cli.main(['--user','2','--status','shipped']); orders_cli.main(['--user','1']); assert order_service.ORDERS==before"
        run=subprocess.run([sys.executable,'-B','-c',code],cwd=PROJECT,capture_output=True,text=True,timeout=10)
        self.assertEqual(run.returncode,0,run.stderr)


if __name__=='__main__':
    unittest.main()
