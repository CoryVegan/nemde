"""Test that model runs correctly"""

import os
import json
import time
import logging
import calendar

import pytest
import numpy as np

import context
from nemde.core.model.execution import run_model
from nemde.io.database import mysql
from nemde.io.casefile import load_base_case
from nemde.config.setup_variables import setup_environment_variables
setup_environment_variables()

logger = logging.getLogger(__name__)


def get_randomised_casefile_ids(year, month, n):
    """
    Get casefile IDs

    Parameters
    ----------
    year : int
        Sample year

    month : int
        Sample month

    n : int
        Number of casefiles to return

    Returns
    -------
    Shuffled list of casefile IDs
    """

    # Get days in specified month
    _, days_in_month = calendar.monthrange(year, month)

    # Seed random number generator for reproducable results
    np.random.seed(10)

    # Population of dispatch intervals for a given month
    population = [f'{year}{month:02}{i:02}{j:03}'
                  for i in range(1, days_in_month + 1) for j in range(1, 289)]

    # Shuffle list to randomise sample (should be reproducible though because seed is set)
    np.random.shuffle(population)

    return population[:n]


def get_casefile_ids():
    """Run tests for a given set of casefiles"""

    # Cases where at least one trader has current mode = 1
    # case_ids = ['20201101017', '20201101126', '20201101127', '20201101134',
    #             '20201101135', '20201101161', '20201101164', '20201101165',
    #             '20201101169']

    # # Cases where at least one trader has current mode = 2
    # case_ids = ['20201101076',
    #             '20201101136',
    #             '20201101159',
    #             '20201101160',
    #             '20201101160',
    #             '20201101161',
    #             '20201101165',
    #             '20201101166',
    #             '20201101167',
    #             '20201101171',
    #             '20201101172',
    #             '20201101173']

    # # Cases where pass criterion should fail
    # case_ids = ['20201117113']

    # Cases where fast start generator starts up
    case_ids = [
        '20201117111',
        # '20201120224',
        ]

    return case_ids


# @pytest.fixture(scope='module', params=get_randomised_casefile_ids(year=2020, month=11, n=2000))
@pytest.fixture(scope='module', params=get_casefile_ids())
def case_id(request):
    return request.param


def test_run_model():
    """Test model runs correctly given user input"""

    user_data_dict = {
        'case_id': '20201101001',
        'run_mode': 'physical'
    }

    # Run model
    user_data_json = json.dumps(user_data_dict)
    solution = run_model(user_data=user_data_json)

    # Extract total objective obtained from model
    model_objective = solution['PeriodSolution']['@TotalObjective']

    # Check NEMDE solution for the corresponding dispatch interval
    base_case = load_base_case(case_id=user_data_dict['case_id'])
    nemde_objective = float(base_case.get('NEMSPDCaseFile')
                            .get('NemSpdOutputs').get('PeriodSolution')
                            .get('@TotalObjective'))

    # Normalised difference between model and observed objectives
    relative_difference = (model_objective - nemde_objective) / nemde_objective

    assert abs(relative_difference) <= 1e-3


def test_run_model_validation(testrun_uid, case_id):
    """Run model for a sample of case IDs"""

    user_data = {
        'case_id': case_id,
        'run_mode': 'physical',
        'options': {
            'algorithm': 'dispatch_only',
            'solution_format': 'validation'
        }
    }

    # Run model and return solution
    user_data_json = json.dumps(user_data)
    solution = run_model(user_data=user_data_json)

    # Entry to post to database
    entry = {
        'run_id': testrun_uid,
        'run_time': int(time.time()),
        'case_id': user_data['case_id'],
        'results': json.dumps(solution)
    }

    # Post entry to database
    mysql.post_entry(schema=os.environ['MYSQL_SCHEMA'], table='results', entry=entry)

    # Compute relative difference
    objective = [i for i in solution['PeriodSolution']
                 if i['key'] == '@TotalObjective'][0]
    absolute_difference = abs(objective['model'] - objective['actual'])
    relative_difference = absolute_difference / abs(objective['actual'])

    assert relative_difference <= 0.001
