"""Run published instructor checks against a selected local practice project."""
import argparse
import datetime
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import unittest


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def add_import_error(suite,error,label):
    def fail(error=error):
        raise error
    suite.addTest(unittest.FunctionTestCase(fail,description=label))


def main():
    parser=argparse.ArgumentParser(description='Check course behavior; does not assess your explanation or certify AI use.')
    parser.add_argument('project',type=Path)
    parser.add_argument('--stage',choices=['cli','capstone'],default='cli')
    parser.add_argument('--report',type=Path)
    parser.add_argument('--verbose',action='store_true',help='Print full check output as well as saving it in the report')
    args=parser.parse_args()
    project=args.project.resolve();base=Path(__file__).resolve().parent
    expected=json.loads((base/'expected-files.json').read_text())
    files={name:hashlib.sha256((project/name).read_bytes()).hexdigest() if (project/name).is_file() else None for name in [*expected['frozen_checks'],'order_service.py','orders_cli.py']}
    unchanged=all(files[name]==digest for name,digest in expected['frozen_checks'].items())
    service_ok=args.stage!='cli' or files['order_service.py']==expected['status_service_sha256']
    os.environ['COURSE_SUBMISSION_DIR']=str(project)
    sys.path.insert(0,str(project))
    stream=io.StringIO();suite=unittest.TestSuite()
    loader=unittest.TestLoader()
    for i,path in enumerate(sorted((base/'frozen').glob('test_*.py'))):
        try:
            suite.addTests(loader.loadTestsFromModule(load_module('frozen_course_'+str(i),path)))
        except (Exception,SystemExit) as error:
            add_import_error(suite,error,'Cannot load frozen checks: '+path.name)
    cli=load_module('cli_acceptance',base/'cli_acceptance.py')
    suite.addTests(loader.loadTestsFromTestCase(cli.CLIAcceptance))
    if args.stage=='capstone':
        try:
            keyword=load_module('keyword_acceptance',base/'keyword_acceptance.py')
            suite.addTests(loader.loadTestsFromTestCase(keyword.KeywordAcceptance))
            for name in sorted(keyword.CLIKeywordAcceptance.__dict__):
                if name.startswith('test_keyword_cli_'):suite.addTest(keyword.CLIKeywordAcceptance(name))
        except (Exception,SystemExit) as error:
            add_import_error(suite,error,'Cannot load keyword checks')
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    passed=result.wasSuccessful() and unchanged and service_ok and not result.skipped and not result.expectedFailures
    report=dict(checked_at=datetime.datetime.now().astimezone().isoformat(),project=str(project),stage=args.stage,checks_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),frozen_checks_unchanged=unchanged,status_service_unchanged_for_cli_stage=service_ok,behavioral_checks_passed=passed,files_sha256=files,output=stream.getvalue(),ai_interaction_verified=False,understanding_assessed=False,publication=False)
    print(f"{args.stage}: {result.testsRun} checks; {len(result.failures)} failures; {len(result.errors)} errors")
    if args.verbose:print(stream.getvalue())
    elif not passed:
        for test,_ in [*result.failures,*result.errors]:print('REVIEW',test.id())
        if not (project/'orders_cli.py').is_file():print('NEXT: implement orders_cli.py against the contract. Missing CLI behavior is expected before that exercise.')
        print('Full details are in --report output; use --verbose to print them.')
    print('FROZEN_CHECKS_UNCHANGED',unchanged)
    print('STATUS_SERVICE_UNCHANGED_FOR_CLI_STAGE',service_ok)
    print('BEHAVIORAL_CHECKS_PASSED',passed)
    print('Your actual AI session, diff explanation and handoff still need review.')
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return 0 if passed else 1


if __name__=='__main__':
    raise SystemExit(main())
