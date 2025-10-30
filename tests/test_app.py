import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that the root endpoint redirects to index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities

def test_signup_for_activity_success():
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"

    # Verify the participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_for_activity_duplicate():
    """Test duplicate signup prevention"""
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    
    # Try to signup again
    response = client.post("/activities/Programming Class/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()

def test_signup_for_nonexistent_activity():
    """Test signup for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_signup_when_activity_is_full():
    """Test signup when activity is at max capacity"""
    # Fill up an activity to max capacity
    activity_name = "Chess Club"
    activities = client.get("/activities").json()
    max_participants = activities[activity_name]["max_participants"]
    current_participants = len(activities[activity_name]["participants"])
    
    # Add participants until full
    for i in range(current_participants, max_participants):
        client.post(f"/activities/{activity_name}/signup?email=student{i}@mergington.edu")
    
    # Try to add one more participant
    response = client.post(f"/activities/{activity_name}/signup?email=extra@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()

def test_unregister_from_activity_success():
    """Test successful unregistration from activity"""
    # First sign up
    email = "unregister_test@mergington.edu"
    activity = "Drama Club"
    client.post(f"/activities/{activity}/signup?email={email}")
    
    # Then unregister
    response = client.post(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregistration when not registered"""
    response = client.post("/activities/Art Studio/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"].lower()

def test_unregister_from_nonexistent_activity():
    """Test unregistration from non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()