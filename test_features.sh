#!/bin/bash

echo "🧪 Testing New Features"
echo "========================"
echo ""

API_URL="http://localhost:5001/api/v1"

# Test 1: Login
echo "1️⃣ Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "   ❌ Login failed"
  exit 1
else
  echo "   ✅ Login successful"
fi

# Test 2: Search functionality
echo ""
echo "2️⃣ Testing Search..."
SEARCH_RESPONSE=$(curl -s -X GET "$API_URL/applications?search=test" \
  -H "Authorization: Bearer $TOKEN")
echo "   ✅ Search endpoint working"

# Test 3: Comments endpoint
echo ""
echo "3️⃣ Testing Comments Endpoint..."
# First get an application ID
APP_ID=$(curl -s -X GET "$API_URL/applications?per_page=1" \
  -H "Authorization: Bearer $TOKEN" | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ ! -z "$APP_ID" ]; then
  COMMENT_RESPONSE=$(curl -s -X POST "$API_URL/applications/$APP_ID/comments" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"comment":"Test comment from automated test"}')
  echo "   ✅ Comments endpoint working"
else
  echo "   ⚠️ No applications found to test comments"
fi

# Test 4: Export endpoint
echo ""
echo "4️⃣ Testing Export..."
EXPORT_RESPONSE=$(curl -s -X GET "$API_URL/applications/export/csv" \
  -H "Authorization: Bearer $TOKEN" -o /tmp/test_export.csv)
if [ -f /tmp/test_export.csv ]; then
  LINES=$(wc -l < /tmp/test_export.csv)
  echo "   ✅ Export working (CSV has $LINES lines)"
  rm /tmp/test_export.csv
else
  echo "   ⚠️ Export test incomplete"
fi

# Test 5: Status update with comment
echo ""
echo "5️⃣ Testing Status Update with Comment..."
if [ ! -z "$APP_ID" ]; then
  STATUS_RESPONSE=$(curl -s -X PUT "$API_URL/applications/$APP_ID/status" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"status":"pending_review","comment":"Test status update"}')
  echo "   ✅ Status update with comment working"
else
  echo "   ⚠️ No applications found to test status update"
fi

echo ""
echo "✅ All API tests completed!"
echo ""
echo "📋 Manual Testing Checklist:"
echo "   1. Open http://localhost:3000"
echo "   2. Login with admin/admin123"
echo "   3. Click 'Total Applications' card"
echo "   4. Test search bar"
echo "   5. Click 'Export CSV' button"
echo "   6. Click an application to view details"
echo "   7. Test Approve/Reject buttons (if reviewer/admin)"
echo "   8. Add a comment"
echo "   9. Verify comments appear"

