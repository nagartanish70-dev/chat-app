# Chat Application - Quick Start Guide

## What's New? ✨
Your FastAPI backend now includes a complete chat application with:
- User authentication & signup
- Real-time messaging
- **📎 File sharing (photos, videos, documents up to 200MB)**
- **🟢 Online/Offline status indicators**
- **💾 Session persistence (stay logged in after refresh)**

## Features:
✅ User signup and login with password hashing
✅ Unique usernames (no duplicates allowed)
✅ Search for users by username
✅ Real-time messaging between users
✅ **Share images, videos, and files (max 200MB)**
✅ **See who's online in real-time**
✅ **Stay logged in even after page refresh**
✅ Conversation history
✅ Automatic message refresh
✅ Modern, responsive UI

## How to Use:

### 1. Start the Backend Server
Open PowerShell and run:
```
cd D:\ggeg
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
Keep this terminal open while using the chat.

### 2. Open the Chat Application
Open `chat.html` in your web browser.

**Good news:** You'll stay logged in even if you refresh or close the browser!

### 3. Create an Account
- Click "Don't have an account? Sign up"
- Enter a unique username (at least 3 characters)
- Enter a password (at least 4 characters)
- Click "Sign Up"

### 4. Start Chatting
- Use the search box to find other users
- **Green dot = online, Gray dot = offline**
- Click on a username to start a conversation
- Type your message and click "Send" or press Enter
- **Click the 📎 button to attach photos, videos, or files**
- Messages refresh automatically every 2 seconds

### 5. Sharing Files
- Click the paperclip (📎) button next to the message input
- Select any file up to 200MB
- Preview appears - click "Cancel" to remove or just send
- Supported: Images, videos, documents, any file type
- Images and videos are displayed inline
- Other files show as download links

## Files Created:
- `chat.html` - The chat application frontend
- `users.json` - Stores all registered users
- `messages.json` - Stores all chat messages
- `online_users.json` - Tracks online/offline status
- `chat_files/` - Directory for uploaded chat files

## New API Endpoints:
- `POST /signup` - Create a new user account
- `POST /login` - Login to an existing account
- `POST /logout/{username}` - Logout and set status to offline
- `POST /heartbeat/{username}` - Keep user online (sent every 30 seconds)
- `GET /search_users/{query}` - Search for users
- `POST /send_message` - Send a message (with optional file attachment)
- `POST /upload_chat_file` - Upload a file for chat (max 200MB)
- `GET /download_chat_file/{filename}` - Download a chat file
- `GET /get_messages/{user1}/{user2}` - Get conversation between two users
- `GET /get_conversations/{username}` - Get all conversations for a user
- `GET /online_status/{username}` - Get specific user's online status
- `GET /all_online_status` - Get all users' online status

## Technical Details:

### Session Persistence:
- Uses browser's localStorage to save login session
- Automatically reconnects when you reopen the browser
- Sends heartbeat every 30 seconds to keep you online
- Status refreshes every 5 seconds

### File Sharing:
- Maximum file size: 200MB
- Supports all file types
- Images: displayed inline with preview
- Videos: embedded video player
- Other files: download link
- Files stored in `chat_files/` directory
- Unique filenames prevent conflicts

### Online Status:
- Real-time status updates
- Shows green dot for online users
- Shows gray dot for offline users
- Updates every 5 seconds
- Last seen timestamp tracked

## Notes:
- All data is stored locally in JSON files
- Passwords are hashed with SHA-256
- Your photo upload app still works at the same backend!
- To make the chat accessible from other devices, use ngrok or port forwarding
- Session persists across browser refreshes and reopens
- Heartbeat keeps you online while the page is open

## Troubleshooting:

### Chat not loading after refresh?
- Check browser console for errors
- Make sure backend server is running
- Try clearing localStorage: `localStorage.clear()` in browser console

### Can't upload files?
- Check file size (must be under 200MB)
- Ensure `chat_files` directory exists in D:\ggeg
- Check backend server logs for errors

### Online status not updating?
- Backend must be running
- Check if `online_users.json` exists
- Try logging out and back in

### General issues:
1. Make sure the backend server is running on port 8000
2. Check the browser console for errors (F12 > Console)
3. Verify all JSON files are created in D:\ggeg
4. Try clearing your browser cache

Enjoy your enhanced chat application with file sharing and online status! 🎉
