# Frontend Update Troubleshooting

## If changes aren't showing:

### 1. Hard Refresh Browser
- **Chrome/Edge**: `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)
- **Firefox**: `Ctrl + F5` (Windows) or `Cmd + Shift + R` (Mac)
- **Safari**: `Cmd + Option + R`

### 2. Clear Browser Cache
- Open DevTools (F12)
- Right-click the refresh button
- Select "Empty Cache and Hard Reload"

### 3. Check Browser Console
- Open DevTools (F12)
- Check Console tab for errors
- Check Network tab to see if CSS files are loading

### 4. Verify CSS Variables
Open browser console and run:
```javascript
getComputedStyle(document.documentElement).getPropertyValue('--primary')
```
Should return: `#030213`

### 5. Restart Dev Server
If still not working:
```bash
cd frontend
# Stop the server (Ctrl+C)
npm start
```

### 6. Check File Changes
Verify the files were saved:
- `frontend/src/index.css` - Should have CSS variables
- `frontend/src/App.jsx` - Should use `style={{ color: 'var(--primary)' }}`

## Expected Changes

After update, you should see:
- **Navbar**: Dark primary color (#030213) instead of indigo
- **Background**: White instead of gradient
- **Inputs**: Light gray background (#f3f3f5)
- **Buttons**: Dark primary color
- **Cards**: White with subtle borders

## Still Not Working?

1. Check if there are compilation errors in the terminal
2. Verify the dev server is running on http://localhost:3000
3. Try opening in incognito/private mode
4. Check if any browser extensions are blocking CSS

