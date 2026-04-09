
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
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

def test_signup_and_unregister():
    # Sign up a new participant
    email = "testuser@mergington.edu"
    activity = "Chess Club"
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    assert f"Signed up {email}" in signup_resp.json()["message"]

    # Try duplicate signup
    dup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert dup_resp.status_code == 400 or dup_resp.status_code == 409

    # Unregister the participant
    unreg_resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unreg_resp.status_code == 200
    assert f"Unregistered {email}" in unreg_resp.json()["message"]

    # Try to unregister again (should fail)
    unreg_fail = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert unreg_fail.status_code == 404

def test_signup_activity_not_found():
    resp = client.post("/activities/Nonexistent/signup?email=someone@mergington.edu")
    assert resp.status_code == 404

def test_unregister_activity_not_found():
    resp = client.delete("/activities/Nonexistent/unregister?email=someone@mergington.edu")
    assert resp.status_code == 404
