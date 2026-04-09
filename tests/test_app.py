
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)

# Save the original activities data for test isolation
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities dict before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities():
    # Arrange: nothing to set up, just use the client

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_and_unregister():
    # Arrange
    email = "testuser@mergington.edu"
    activity = "Chess Club"

    # Act: Sign up a new participant
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Signup successful
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json()["message"]

    # Act: Try duplicate signup
    dup_resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: Duplicate signup fails
    assert dup_resp.status_code == 400 or dup_resp.status_code == 409

    # Act: Unregister the participant
    unreg_resp = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert: Unregister successful
    assert unreg_resp.status_code == 200
    assert f"Unregistered {email}" in unreg_resp.json()["message"]

    # Act: Try to unregister again (should fail)
    unreg_fail = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert: Unregister fails with 404
    assert unreg_fail.status_code == 404


def test_signup_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent"

    # Act
    resp = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 404


def test_unregister_activity_not_found():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent"

    # Act
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")

    # Assert
    assert resp.status_code == 404
