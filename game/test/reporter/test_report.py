import json

from .utils import create_random_report


def test_report_serializes_to_json():
    # Given a report
    report = create_random_report()

    # Then the report should serialize to json
    json_str = report.to_json()
    assert isinstance(json_str, str)

    # Then the json string should be correct
    json_dict = json.loads(json_str)
    assert json_dict["container_id"] == str(report.container_id)
    assert json_dict["reward"] == report.reward
    assert json_dict["step_count"] == report.step_count
    assert json_dict["epsilon"] == report.epsilon
    assert json_dict["loss"] == report.loss
    assert json_dict["done"] == report.done
