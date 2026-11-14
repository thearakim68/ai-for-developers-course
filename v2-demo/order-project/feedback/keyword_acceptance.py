"""Instructor-written capstone cases; each requirement is in the public contract."""
import copy
import unittest
from unittest.mock import patch
from order_service import orders_for
from cli_acceptance import CLIAcceptance


class KeywordAcceptance(unittest.TestCase):
    def test_case_and_surrounding_whitespace(self):
        self.assertEqual(orders_for(2,keyword='  MOU  '),[{'id':11,'item':'mouse'}])

    def test_other_owner_is_excluded(self):
        self.assertEqual(orders_for(2,keyword='monitor'),[])

    def test_status_stays_required(self):
        self.assertEqual(orders_for(2,'pending','mouse'),[])

    def test_none_preserves_prior_calls(self):
        self.assertEqual(orders_for(1,keyword=None),orders_for(1))

    def test_no_match(self):
        self.assertEqual(orders_for(2,keyword='lamp'),[])

    def test_blank_keyword_is_rejected(self):
        for keyword in ['', '  ', '\t\n']:
            with self.subTest(keyword=keyword), self.assertRaisesRegex(ValueError,'^empty keyword$'):
                orders_for(2,keyword=keyword)

    def test_non_string_keyword_is_rejected(self):
        for keyword in [12,False,[],{}]:
            with self.subTest(keyword=keyword), self.assertRaisesRegex(ValueError,'^invalid keyword$'):
                orders_for(2,keyword=keyword)

    def test_user_is_validated_before_status_and_keyword(self):
        with self.assertRaisesRegex(ValueError,'^unknown user$'):
            orders_for(99,'lost','')

    def test_status_is_validated_before_keyword(self):
        with self.assertRaisesRegex(ValueError,'^unknown status$'):
            orders_for(2,'lost','')

    def test_whole_result_order_fields_and_source_immutability(self):
        fixture=[dict(id=100,user_id=2,item='Mousepad',status='shipped'),dict(id=20,user_id=1,item='mouse',status='shipped'),dict(id=5,user_id=2,item='mouse',status='shipped'),dict(id=1,user_id=2,item='mouse',status='pending')]
        before=copy.deepcopy(fixture)
        with patch('order_service.ORDERS',fixture):
            self.assertEqual(orders_for(2,'shipped','MOUSE'),[dict(id=100,item='Mousepad'),dict(id=5,item='mouse')])
            self.assertEqual(fixture,before)

    def test_casefold_contract_handles_unicode(self):
        fixture=[dict(id=3,user_id=2,item='Straße map',status='shipped')]
        with patch('order_service.ORDERS',fixture):
            self.assertEqual(orders_for(2,keyword='STRASSE'),[dict(id=3,item='Straße map')])


class CLIKeywordAcceptance(CLIAcceptance):
    # This class is loaded with explicit method names by the feedback runner;
    # inherited CLI checks are executed once in their own suite.
    def test_keyword_cli_case_and_whitespace(self):
        self.assert_result(['--user','2','--keyword',' MOU '],[{'id':11,'item':'mouse'}])

    def test_keyword_cli_other_owner_stays_out(self):
        self.assert_result(['--user','2','--keyword','monitor'],[])

    def test_keyword_cli_status_stays_required(self):
        self.assert_result(['--user','2','--status','pending','--keyword','mouse'],[])

    def test_keyword_cli_blank(self):
        self.assert_service_error(['--user','2','--keyword',''],'empty keyword')

    def test_keyword_cli_user_error_first(self):
        self.assert_service_error(['--user','99','--status','lost','--keyword',''],'unknown user')

    def test_keyword_cli_help_lists_keyword(self):
        run=self.invoke('--help')
        self.assertEqual(run.returncode,0)
        self.assertIn('--keyword',run.stdout)
