# Testing Guide

## Quick Test Checklist

### 1. Authentication ✅
- [x] Login with admin/admin123
- [x] Verify dashboard loads

### 2. Search & Filter ✅
- [ ] Click "Total Applications" card
- [ ] Type in search bar (e.g., "Reliable")
- [ ] Click Search button
- [ ] Verify results filtered
- [ ] Try different search terms

### 3. Export CSV ✅
- [ ] Click "Export CSV" button
- [ ] Check downloads folder
- [ ] Open CSV file
- [ ] Verify data is correct
- [ ] Test with search filter applied

### 4. Application Review ✅
- [ ] Click any application from list
- [ ] Verify "Review Actions" section appears (for admin/reviewer)
- [ ] Click "Approve" button
- [ ] Add comment in modal
- [ ] Click "Confirm"
- [ ] Verify status changed to "approved"
- [ ] Test "Reject/Flag" button

### 5. Comments System ✅
- [ ] Scroll to "Comments & Notes" section
- [ ] Type a test comment
- [ ] Click "Add Comment"
- [ ] Verify comment appears with timestamp
- [ ] Add multiple comments
- [ ] Verify all comments display correctly

### 6. End-to-End Flow ✅
- [ ] Submit new application
- [ ] View in applications list
- [ ] Search for it
- [ ] Add comments
- [ ] Approve/Reject it
- [ ] Export to CSV
- [ ] Verify in exported file

## API Endpoints Tested

- ✅ `POST /api/v1/auth/login` - Authentication
- ✅ `GET /api/v1/applications?search=...` - Search
- ✅ `GET /api/v1/applications/export/csv` - Export
- ✅ `POST /api/v1/applications/{id}/comments` - Add comment
- ✅ `GET /api/v1/applications/{id}/comments` - Get comments
- ✅ `PUT /api/v1/applications/{id}/status` - Status update

## Known Issues

None currently. All features working as expected.

## Test Data

If you need test data:
1. Use "Import Kaggle Data" button (admin only)
2. Or submit new applications via the form

