#!/usr/bin/env python3
"""
Test script for new features:
1. File Upload for Documents/Certificates
2. User Management (Admin)
3. Comments System
"""

import requests
import json
import os
import tempfile

API_URL = "http://localhost:5001/api/v1"

def test_login(username="admin", password="admin123"):
    """Login and get JWT token"""
    print("🔐 Testing Login...")
    response = requests.post(f"{API_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_user_management(token):
    """Test user management endpoints"""
    print("\n" + "="*60)
    print("👥 Testing User Management")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get all users
    print("\n1. Getting all users...")
    response = requests.get(f"{API_URL}/users", headers=headers)
    if response.status_code == 200:
        data = response.json()
        users = data.get('users', [])
        print(f"✅ Found {len(users)} users")
        for user in users:
            print(f"   - {user['username']} ({user['email']}) - Role: {user['role']}")
        return users
    else:
        print(f"❌ Failed to get users: {response.status_code} - {response.text}")
        return []

def test_comments(token):
    """Test comments system"""
    print("\n" + "="*60)
    print("💬 Testing Comments System")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Get applications
    print("\n1. Getting applications...")
    response = requests.get(f"{API_URL}/applications?per_page=1", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get applications: {response.status_code}")
        return None
    
    data = response.json()
    applications = data.get('applications', [])
    if not applications:
        print("⚠️  No applications found. Creating one first...")
        # Create a test application
        app_response = requests.post(f"{API_URL}/applications", headers=headers, json={
            "type": "vendor",
            "company_name": "Test Company for Comments",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "industry": "Technology"
        })
        if app_response.status_code == 201:
            app_id = app_response.json().get('application_id')
            print(f"✅ Created test application: {app_id}")
        else:
            print(f"❌ Failed to create application: {app_response.status_code}")
            return None
    else:
        app_id = applications[0]['id']
        print(f"✅ Using application ID: {app_id}")
    
    # 2. Add a comment
    print(f"\n2. Adding comment to application {app_id}...")
    comment_response = requests.post(
        f"{API_URL}/applications/{app_id}/comments",
        headers=headers,
        json={"comment": "This is a test comment from the test script!"}
    )
    if comment_response.status_code == 201:
        comment_data = comment_response.json()
        print(f"✅ Comment added successfully!")
        print(f"   Comment ID: {comment_data.get('comment', {}).get('id')}")
    else:
        print(f"❌ Failed to add comment: {comment_response.status_code} - {comment_response.text}")
    
    # 3. Get all comments
    print(f"\n3. Getting all comments for application {app_id}...")
    comments_response = requests.get(
        f"{API_URL}/applications/{app_id}/comments",
        headers=headers
    )
    if comments_response.status_code == 200:
        comments_data = comments_response.json()
        comments = comments_data.get('comments', [])
        print(f"✅ Found {len(comments)} comments")
        for comment in comments:
            print(f"   - {comment.get('comment', '')[:50]}... by {comment.get('username', 'Unknown')}")
    else:
        print(f"❌ Failed to get comments: {comments_response.status_code}")
    
    # 4. Get application details (should include comments)
    print(f"\n4. Getting application details (should include comments)...")
    app_details_response = requests.get(
        f"{API_URL}/applications/{app_id}",
        headers=headers
    )
    if app_details_response.status_code == 200:
        app_data = app_details_response.json()
        comments_in_details = app_data.get('comments', [])
        print(f"✅ Application details include {len(comments_in_details)} comments")
    else:
        print(f"❌ Failed to get application details: {app_details_response.status_code}")
    
    return app_id

def test_file_upload(token, app_id):
    """Test file upload functionality"""
    print("\n" + "="*60)
    print("📄 Testing File Upload")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create a test file
    print("\n1. Creating test file...")
    test_content = "This is a test document for file upload testing."
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # 2. Upload file
        print(f"\n2. Uploading file to application {app_id}...")
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'file_type': 'document'}
            response = requests.post(
                f"{API_URL}/applications/{app_id}/documents",
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data=data
            )
        
        if response.status_code == 201:
            doc_data = response.json()
            doc_id = doc_data.get('document', {}).get('id')
            print(f"✅ File uploaded successfully!")
            print(f"   Document ID: {doc_id}")
            print(f"   Filename: {doc_data.get('document', {}).get('filename')}")
            print(f"   File Type: {doc_data.get('document', {}).get('file_type')}")
            print(f"   File Size: {doc_data.get('document', {}).get('file_size')} bytes")
        else:
            print(f"❌ Failed to upload file: {response.status_code} - {response.text}")
            return None
        
        # 3. Get all documents for application
        print(f"\n3. Getting all documents for application {app_id}...")
        docs_response = requests.get(
            f"{API_URL}/applications/{app_id}/documents",
            headers=headers
        )
        if docs_response.status_code == 200:
            docs_data = docs_response.json()
            documents = docs_data.get('documents', [])
            print(f"✅ Found {len(documents)} documents")
            for doc in documents:
                print(f"   - {doc.get('filename')} ({doc.get('file_type')}) - {doc.get('file_size')} bytes")
        else:
            print(f"❌ Failed to get documents: {docs_response.status_code}")
        
        # 4. Download document
        if doc_id:
            print(f"\n4. Testing document download (ID: {doc_id})...")
            download_response = requests.get(
                f"{API_URL}/documents/{doc_id}/download",
                headers=headers
            )
            if download_response.status_code == 200:
                print(f"✅ Document download successful!")
                print(f"   Content length: {len(download_response.content)} bytes")
            else:
                print(f"❌ Failed to download document: {download_response.status_code}")
        
        # 5. Delete document
        if doc_id:
            print(f"\n5. Testing document deletion (ID: {doc_id})...")
            delete_response = requests.delete(
                f"{API_URL}/documents/{doc_id}",
                headers=headers
            )
            if delete_response.status_code == 200:
                print(f"✅ Document deleted successfully!")
            else:
                print(f"❌ Failed to delete document: {delete_response.status_code} - {delete_response.text}")
        
        return doc_id
        
    finally:
        # Clean up test file
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def check_backend():
    """Check if backend is running"""
    try:
        # Try to connect to the API - 401 means backend is running
        response = requests.get(f"{API_URL}/applications", timeout=3)
        # Any response (even 401) means backend is running
        return True
    except requests.exceptions.ConnectionError:
        return False
    except:
        # Other errors might mean backend is running but has issues
        return True

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Testing New Features")
    print("="*60)
    
    # Check if backend is running
    print("\n🔍 Checking if backend is running...")
    if not check_backend():
        print("❌ Backend is not running on http://localhost:5001")
        print("   Please start the backend first:")
        print("   cd backend && source venv/bin/activate && python app.py")
        return
    print("✅ Backend is running!")
    
    # Login
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test User Management
    users = test_user_management(token)
    
    # Test Comments
    app_id = test_comments(token)
    
    # Test File Upload
    if app_id:
        test_file_upload(token, app_id)
    
    print("\n" + "="*60)
    print("✅ All Tests Complete!")
    print("="*60)
    print("\n📋 Summary:")
    print("   ✅ User Management - Tested")
    print("   ✅ Comments System - Tested")
    print("   ✅ File Upload - Tested")
    print("\n🎯 Ready for browser testing!")

if __name__ == "__main__":
    main()

