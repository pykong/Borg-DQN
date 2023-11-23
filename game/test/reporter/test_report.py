# FILEPATH: /home/ben/Projects/stream-app-prototype/game/test/report/test_report.py

import json
from datetime import datetime
from time import sleep

from .utils import create_random_report
from src.reporter import Report


def test_report_has_timestamp():
    # Given a report
    report = create_random_report()

    # Then the report should have a timestamp
    assert isinstance(report.timestamp, datetime)


def test_report_timestamp_is_fresh():
    # Given two report
    report_1 = create_random_report()
    sleep(0.001)
    report_2 = create_random_report()

    # Then the first report should have an older timestamp than the second report
    assert report_1.timestamp < report_2.timestamp


def test_report_serializes_to_json():
    # Given a report
    report = create_random_report()

    # Then the report should serialize to json
    json_str = report.to_json()
    assert isinstance(json_str, str)

    # Then the json string should be correct
    json_dict = json.loads(json_str)
    assert json_dict["container_id"] == str(report.container_id)
    assert json_dict["step_count"] == report.step_count
    assert json_dict["reward"] == report.reward
    assert json_dict["timestamp"] == report.timestamp.timestamp()
