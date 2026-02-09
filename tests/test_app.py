"""
Unit tests for the Mergington High School Activities API
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check that expected activities exist
        assert "Tennis Club" in data
        assert "Basketball Team" in data
        assert "Chess Club" in data

    def test_activity_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activity_participants_is_list(self, client):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_data in data.values():
            assert isinstance(activity_data["participants"], list)
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_success(self, client):
        """Test successful signup for an activity"""
        email = "newstudent@mergington.edu"
        activity_name = "Tennis Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_for_nonexistent_activity_fails(self, client):
        """Test that signup for nonexistent activity returns 404"""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_fails(self, client):
        """Test that signing up twice for same activity fails"""
        email = "duplicate_test@mergington.edu"
        activity_name = "Tennis Club"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds participant to activity"""
        email = "verify_signup@mergington.edu"
        activity_name = "Basketball Team"
        
        # Get initial participant count
        before = client.get("/activities")
        before_count = len(before.json()[activity_name]["participants"])
        
        # Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get updated participant count
        after = client.get("/activities")
        after_count = len(after.json()[activity_name]["participants"])
        
        assert after_count == before_count + 1
        assert email in after.json()[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        email = "unregister_test@mergington.edu"
        activity_name = "Art Studio"
        
        # First signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test that unregister from nonexistent activity returns 404"""
        email = "student@mergington.edu"
        activity_name = "Nonexistent Club"
        
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 404

    def test_unregister_not_signed_up_fails(self, client):
        """Test that unregistering when not signed up fails"""
        email = "not_signed_up@mergington.edu"
        activity_name = "Drama Club"
        
        response = client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from activity"""
        email = "remove_verify@mergington.edu"
        activity_name = "Robotics Club"
        
        # Signup
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Get initial count
        before = client.get("/activities")
        before_count = len(before.json()[activity_name]["participants"])
        assert email in before.json()[activity_name]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Verify participant was removed
        after = client.get("/activities")
        after_count = len(after.json()[activity_name]["participants"])
        
        assert after_count == before_count - 1
        assert email not in after.json()[activity_name]["participants"]


class TestRootEndpoint:
    """Tests for the GET / endpoint"""

    def test_root_redirects(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
