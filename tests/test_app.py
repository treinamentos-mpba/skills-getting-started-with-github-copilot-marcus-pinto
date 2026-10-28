from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = deepcopy(app_module.activities)
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()


def test_signup_adds_participant_to_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "new-student@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert signup_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "new-student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant_from_activity(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )
    activities_response = client.get("/activities")

    # Assert
    assert unregister_response.status_code == 200
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"