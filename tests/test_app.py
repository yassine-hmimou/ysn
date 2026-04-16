from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test GET /activities returns the activities data"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup():
    """Test POST /activities/{name}/signup adds a participant"""
    email = "signup_test@example.com"
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in result["message"]
    
    # Verify added to activities
    response = client.get("/activities")
    data = response.json()
    assert email in data["Chess Club"]["participants"]


def test_signup_invalid_activity():
    """Test POST signup with invalid activity name"""
    response = client.post("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_duplicate_signup():
    """Test that duplicate signups are allowed (current behavior)"""
    email = "duplicate_test@example.com"
    # First signup
    client.post(f"/activities/Chess Club/signup?email={email}")
    # Second signup (duplicate)
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200  # Currently allows duplicates
    
    # Verify two entries
    response = client.get("/activities")
    data = response.json()
    count = data["Chess Club"]["participants"].count(email)
    assert count == 2


def test_delete_signup():
    """Test DELETE /activities/{name}/signup removes a participant"""
    email = "delete_test@example.com"
    # First signup
    client.post(f"/activities/Chess Club/signup?email={email}")
    
    # Then delete
    response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email in result["message"]
    
    # Verify removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data["Chess Club"]["participants"]


def test_delete_signup_invalid_activity():
    """Test DELETE signup with invalid activity name"""
    response = client.delete("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]


def test_delete_nonexistent_participant():
    """Test DELETE signup for participant not in activity"""
    response = client.delete("/activities/Chess Club/signup?email=nonexistent@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Participant not found" in result["detail"]


def test_root_redirect():
    """Test GET / redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]