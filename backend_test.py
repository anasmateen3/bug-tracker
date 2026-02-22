#!/usr/bin/env python3
"""
Bug Tracker Backend API Test Suite

This comprehensive test suite covers all API endpoints including:
- Authentication (register, login, me)
- Project management (CRUD operations)  
- Ticket management (CRUD, status updates)
- Comments system
- File attachments
- User management
- Access control and error handling
"""

import requests
import json
import sys
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class BugTrackerAPITester:
    def __init__(self, base_url="https://kanban-hub-10.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.test_data = {}
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def log_test(self, test_name: str, success: bool, response=None, error_msg=None):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests.append({
                'test': test_name,
                'error': error_msg or 'Unknown error',
                'response': response.text if response else None
            })
            print(f"❌ {test_name} - {error_msg}")

    def make_request(self, method: str, endpoint: str, data=None, files=None, expected_status=200) -> tuple:
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        if data and not files:
            headers['Content-Type'] = 'application/json'
            data = json.dumps(data) if isinstance(data, dict) else data

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, headers={k:v for k,v in headers.items() if k != 'Content-Type'}, data=data, files=files)
                else:
                    response = requests.post(url, headers=headers, data=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                return False, None
                
            success = response.status_code == expected_status
            return success, response
            
        except Exception as e:
            return False, str(e)

    # ============= AUTHENTICATION TESTS =============
    
    def test_user_registration(self):
        """Test user registration with different roles"""
        timestamp = int(datetime.now().timestamp())
        
        # Test successful registration
        user_data = {
            "name": f"Test User {timestamp}",
            "email": f"testuser{timestamp}@example.com", 
            "password": "testpass123",
            "role": "developer"
        }
        
        success, response = self.make_request('POST', 'auth/register', user_data, expected_status=200)
        
        if success and response:
            response_data = response.json()
            if 'token' in response_data and 'user' in response_data:
                self.token = response_data['token']
                self.user_id = response_data['user']['id']
                self.test_data['test_user'] = user_data
                self.log_test("User Registration", True)
            else:
                self.log_test("User Registration", False, response, "Missing token or user in response")
        else:
            self.log_test("User Registration", False, response, "Registration failed")

        # Test duplicate email registration
        success, response = self.make_request('POST', 'auth/register', user_data, expected_status=400)
        self.log_test("Duplicate Email Registration (should fail)", success, response, 
                      "Should return 400 for duplicate email")

    def test_user_login(self):
        """Test user login functionality"""
        if 'test_user' not in self.test_data:
            self.log_test("User Login", False, None, "No test user available")
            return
            
        user_data = self.test_data['test_user']
        login_data = {
            "email": user_data['email'],
            "password": user_data['password']
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, expected_status=200)
        
        if success and response:
            response_data = response.json()
            if 'token' in response_data:
                self.log_test("User Login", True)
            else:
                self.log_test("User Login", False, response, "No token in login response")
        else:
            self.log_test("User Login", False, response, "Login failed")

        # Test invalid credentials
        invalid_data = {
            "email": user_data['email'],
            "password": "wrongpassword"
        }
        
        success, response = self.make_request('POST', 'auth/login', invalid_data, expected_status=401)
        self.log_test("Invalid Credentials Login (should fail)", success, response, 
                      "Should return 401 for invalid credentials")

    def test_get_current_user(self):
        """Test getting current user info"""
        if not self.token:
            self.log_test("Get Current User", False, None, "No token available")
            return
            
        success, response = self.make_request('GET', 'auth/me', expected_status=200)
        
        if success and response:
            user_data = response.json()
            if 'email' in user_data and 'name' in user_data:
                self.log_test("Get Current User", True)
            else:
                self.log_test("Get Current User", False, response, "Missing user data fields")
        else:
            self.log_test("Get Current User", False, response, "Failed to get current user")

    # ============= PROJECT MANAGEMENT TESTS =============

    def test_create_project(self):
        """Test project creation"""
        if not self.token:
            self.log_test("Create Project", False, None, "No authentication token")
            return
            
        timestamp = int(datetime.now().timestamp())
        project_data = {
            "name": f"Test Project {timestamp}",
            "description": "A test project for API testing",
            "key": f"TEST{timestamp % 1000}"
        }
        
        success, response = self.make_request('POST', 'projects', project_data, expected_status=200)
        
        if success and response:
            project = response.json()
            if 'id' in project and 'key' in project:
                self.test_data['test_project'] = project
                self.log_test("Create Project", True)
            else:
                self.log_test("Create Project", False, response, "Missing project fields")
        else:
            self.log_test("Create Project", False, response, "Project creation failed")

    def test_get_projects(self):
        """Test fetching projects list"""
        if not self.token:
            self.log_test("Get Projects", False, None, "No authentication token")
            return
            
        success, response = self.make_request('GET', 'projects', expected_status=200)
        
        if success and response:
            projects = response.json()
            if isinstance(projects, list):
                self.log_test("Get Projects", True)
                print(f"   Found {len(projects)} projects")
            else:
                self.log_test("Get Projects", False, response, "Response is not a list")
        else:
            self.log_test("Get Projects", False, response, "Failed to fetch projects")

    def test_get_project_details(self):
        """Test fetching specific project details"""
        if 'test_project' not in self.test_data:
            self.log_test("Get Project Details", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        success, response = self.make_request('GET', f'projects/{project_id}', expected_status=200)
        
        if success and response:
            project = response.json()
            if project['id'] == project_id:
                self.log_test("Get Project Details", True)
            else:
                self.log_test("Get Project Details", False, response, "Project ID mismatch")
        else:
            self.log_test("Get Project Details", False, response, "Failed to get project details")

    def test_update_project(self):
        """Test updating project"""
        if 'test_project' not in self.test_data:
            self.log_test("Update Project", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        update_data = {
            "description": "Updated description for testing"
        }
        
        success, response = self.make_request('PUT', f'projects/{project_id}', update_data, expected_status=200)
        
        if success and response:
            project = response.json()
            if project.get('description') == update_data['description']:
                self.log_test("Update Project", True)
            else:
                self.log_test("Update Project", False, response, "Description not updated")
        else:
            self.log_test("Update Project", False, response, "Project update failed")

    # ============= TICKET MANAGEMENT TESTS =============

    def test_create_ticket(self):
        """Test ticket creation"""
        if 'test_project' not in self.test_data:
            self.log_test("Create Ticket", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        ticket_data = {
            "title": "Test Bug - Login Issue",
            "description": "User cannot login with valid credentials",
            "priority": "high",
            "status": "todo",
            "project_id": project_id
        }
        
        success, response = self.make_request('POST', 'tickets', ticket_data, expected_status=200)
        
        if success and response:
            ticket = response.json()
            if 'id' in ticket and ticket['title'] == ticket_data['title']:
                self.test_data['test_ticket'] = ticket
                self.log_test("Create Ticket", True)
            else:
                self.log_test("Create Ticket", False, response, "Missing ticket fields")
        else:
            self.log_test("Create Ticket", False, response, "Ticket creation failed")

    def test_get_tickets(self):
        """Test fetching tickets"""
        if 'test_project' not in self.test_data:
            self.log_test("Get Tickets", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        success, response = self.make_request('GET', f'tickets?project_id={project_id}', expected_status=200)
        
        if success and response:
            tickets = response.json()
            if isinstance(tickets, list):
                self.log_test("Get Tickets", True)
                print(f"   Found {len(tickets)} tickets")
            else:
                self.log_test("Get Tickets", False, response, "Response is not a list")
        else:
            self.log_test("Get Tickets", False, response, "Failed to fetch tickets")

    def test_get_ticket_details(self):
        """Test fetching specific ticket details"""
        if 'test_ticket' not in self.test_data:
            self.log_test("Get Ticket Details", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        success, response = self.make_request('GET', f'tickets/{ticket_id}', expected_status=200)
        
        if success and response:
            ticket = response.json()
            if ticket['id'] == ticket_id:
                self.log_test("Get Ticket Details", True)
            else:
                self.log_test("Get Ticket Details", False, response, "Ticket ID mismatch")
        else:
            self.log_test("Get Ticket Details", False, response, "Failed to get ticket details")

    def test_update_ticket(self):
        """Test updating ticket"""
        if 'test_ticket' not in self.test_data:
            self.log_test("Update Ticket", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        update_data = {
            "status": "inprogress",
            "priority": "critical"
        }
        
        success, response = self.make_request('PUT', f'tickets/{ticket_id}', update_data, expected_status=200)
        
        if success and response:
            ticket = response.json()
            if ticket.get('status') == 'inprogress' and ticket.get('priority') == 'critical':
                self.log_test("Update Ticket", True)
            else:
                self.log_test("Update Ticket", False, response, "Ticket not properly updated")
        else:
            self.log_test("Update Ticket", False, response, "Ticket update failed")

    def test_ticket_filtering(self):
        """Test ticket filtering functionality"""
        if 'test_project' not in self.test_data:
            self.log_test("Ticket Filtering", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        
        # Test filter by status
        success, response = self.make_request('GET', f'tickets?project_id={project_id}&status=inprogress', expected_status=200)
        if success:
            self.log_test("Filter Tickets by Status", True)
        else:
            self.log_test("Filter Tickets by Status", False, response, "Status filtering failed")
        
        # Test search functionality
        success, response = self.make_request('GET', f'tickets?project_id={project_id}&search=Login', expected_status=200)
        if success:
            self.log_test("Search Tickets", True)
        else:
            self.log_test("Search Tickets", False, response, "Ticket search failed")

    # ============= COMMENT SYSTEM TESTS =============

    def test_create_comment(self):
        """Test adding comments to tickets"""
        if 'test_ticket' not in self.test_data:
            self.log_test("Create Comment", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        comment_data = {
            "ticket_id": ticket_id,
            "text": "This is a test comment for the ticket"
        }
        
        success, response = self.make_request('POST', 'comments', comment_data, expected_status=200)
        
        if success and response:
            comment = response.json()
            if 'id' in comment and comment['text'] == comment_data['text']:
                self.test_data['test_comment'] = comment
                self.log_test("Create Comment", True)
            else:
                self.log_test("Create Comment", False, response, "Comment creation failed")
        else:
            self.log_test("Create Comment", False, response, "Failed to create comment")

    def test_get_comments(self):
        """Test fetching comments for a ticket"""
        if 'test_ticket' not in self.test_data:
            self.log_test("Get Comments", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        success, response = self.make_request('GET', f'comments?ticket_id={ticket_id}', expected_status=200)
        
        if success and response:
            comments = response.json()
            if isinstance(comments, list):
                self.log_test("Get Comments", True)
                print(f"   Found {len(comments)} comments")
            else:
                self.log_test("Get Comments", False, response, "Response is not a list")
        else:
            self.log_test("Get Comments", False, response, "Failed to fetch comments")

    # ============= USER MANAGEMENT TESTS =============

    def test_get_users(self):
        """Test fetching all users"""
        if not self.token:
            self.log_test("Get Users", False, None, "No authentication token")
            return
            
        success, response = self.make_request('GET', 'users', expected_status=200)
        
        if success and response:
            users = response.json()
            if isinstance(users, list):
                self.log_test("Get Users", True)
                print(f"   Found {len(users)} users")
            else:
                self.log_test("Get Users", False, response, "Response is not a list")
        else:
            self.log_test("Get Users", False, response, "Failed to fetch users")

    # ============= ATTACHMENT TESTS =============

    def test_file_attachment(self):
        """Test file attachment functionality"""
        if 'test_ticket' not in self.test_data:
            self.log_test("File Attachment", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        
        # Create a simple test file
        test_content = b"This is a test file content for attachment testing"
        files = {'file': ('test_file.txt', test_content, 'text/plain')}
        
        success, response = self.make_request('POST', f'tickets/{ticket_id}/attachments', 
                                            data=None, files=files, expected_status=200)
        
        if success and response:
            self.log_test("File Attachment", True)
        else:
            self.log_test("File Attachment", False, response, "File attachment failed")

    # ============= ACCESS CONTROL TESTS =============

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        # Temporarily remove token
        original_token = self.token
        self.token = None
        
        success, response = self.make_request('GET', 'projects', expected_status=401)
        self.log_test("Unauthorized Access (should fail)", success, response, 
                      "Should return 401 without token")
        
        # Restore token
        self.token = original_token

    def test_invalid_token(self):
        """Test accessing endpoints with invalid token"""
        # Use invalid token
        original_token = self.token
        self.token = "invalid_token_12345"
        
        success, response = self.make_request('GET', 'projects', expected_status=401)
        self.log_test("Invalid Token Access (should fail)", success, response, 
                      "Should return 401 with invalid token")
        
        # Restore token
        self.token = original_token

    # ============= CLEANUP TESTS =============

    def test_delete_comment(self):
        """Test deleting a comment"""
        if 'test_comment' not in self.test_data:
            self.log_test("Delete Comment", False, None, "No test comment available")
            return
            
        comment_id = self.test_data['test_comment']['id']
        success, response = self.make_request('DELETE', f'comments/{comment_id}', expected_status=200)
        
        if success:
            self.log_test("Delete Comment", True)
        else:
            self.log_test("Delete Comment", False, response, "Comment deletion failed")

    def test_delete_ticket(self):
        """Test deleting a ticket"""
        if 'test_ticket' not in self.test_data:
            self.log_test("Delete Ticket", False, None, "No test ticket available")
            return
            
        ticket_id = self.test_data['test_ticket']['id']
        success, response = self.make_request('DELETE', f'tickets/{ticket_id}', expected_status=200)
        
        if success:
            self.log_test("Delete Ticket", True)
        else:
            self.log_test("Delete Ticket", False, response, "Ticket deletion failed")

    def test_delete_project(self):
        """Test deleting a project"""
        if 'test_project' not in self.test_data:
            self.log_test("Delete Project", False, None, "No test project available")
            return
            
        project_id = self.test_data['test_project']['id']
        success, response = self.make_request('DELETE', f'projects/{project_id}', expected_status=200)
        
        if success:
            self.log_test("Delete Project", True)
        else:
            self.log_test("Delete Project", False, response, "Project deletion failed")

    # ============= TEST RUNNER =============

    def run_all_tests(self):
        """Run all test cases in sequence"""
        print("🚀 Starting Bug Tracker API Tests")
        print("=" * 50)
        
        # Authentication Tests
        print("\n📝 Authentication Tests")
        print("-" * 30)
        self.test_user_registration()
        self.test_user_login()
        self.test_get_current_user()
        
        # Project Management Tests  
        print("\n📁 Project Management Tests")
        print("-" * 30)
        self.test_create_project()
        self.test_get_projects()
        self.test_get_project_details()
        self.test_update_project()
        
        # Ticket Management Tests
        print("\n🎫 Ticket Management Tests")
        print("-" * 30)
        self.test_create_ticket()
        self.test_get_tickets()
        self.test_get_ticket_details()
        self.test_update_ticket()
        self.test_ticket_filtering()
        
        # Comment System Tests
        print("\n💬 Comment System Tests")
        print("-" * 30)
        self.test_create_comment()
        self.test_get_comments()
        
        # User Management Tests
        print("\n👥 User Management Tests")
        print("-" * 30)
        self.test_get_users()
        
        # File Attachment Tests
        print("\n📎 File Attachment Tests")
        print("-" * 30)
        self.test_file_attachment()
        
        # Access Control Tests
        print("\n🔒 Access Control Tests")
        print("-" * 30)
        self.test_unauthorized_access()
        self.test_invalid_token()
        
        # Cleanup Tests
        print("\n🗑️ Cleanup Tests")
        print("-" * 30)
        self.test_delete_comment()
        self.test_delete_ticket()
        self.test_delete_project()
        
        self.print_summary()

    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "=" * 50)
        print("🏁 TEST EXECUTION SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for i, failed_test in enumerate(self.failed_tests, 1):
                print(f"{i}. {failed_test['test']}")
                print(f"   Error: {failed_test['error']}")
                if failed_test['response']:
                    print(f"   Response: {failed_test['response'][:200]}...")
                print()
        
        return len(self.failed_tests) == 0

def main():
    """Main function to run the test suite"""
    tester = BugTrackerAPITester()
    
    print("Bug Tracker API Test Suite")
    print(f"Testing against: {tester.api_url}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())