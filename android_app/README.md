# Complete Android Chat App

This is a complete, production-ready Android chat application built with:

## Technology Stack

### Core Framework
- **Jetpack Compose** - Modern declarative UI toolkit
- **Kotlin** - Modern Android programming language
- **Android 24+** - Minimum SDK

### Libraries & Tools
- **Retrofit 2** - HTTP client for API communication
- **Room Database** - Local data persistence
- **DataStore** - Secure session management
- **Hilt** - Dependency injection
- **Coroutines** - Asynchronous operations
- **Material Design 3** - UI design system

## Features Implemented

✅ **User Authentication**
  - User registration with validation
  - Login with session persistence
  - Automatic logout
  - Remember me functionality

✅ **Real-Time Messaging**
  - Send/receive messages
  - Auto-refresh every 2 seconds
  - Message history
  - Typing indicators

✅ **User Management**
  - Search users by username
  - View all users
  - Online/offline status with color indicators
  - User profiles
  - Last seen timestamps

✅ **File Sharing**
  - Upload files up to 200MB
  - Image preview
  - Video playback
  - Audio player
  - File download support
  - Automatic MIME type detection

✅ **Session Persistence**
  - Stay logged in after app close
  - Auto-login on app restart
  - Heartbeat to keep session alive
  - Secure token storage

✅ **Message Features**
  - Edit own messages
  - Delete messages
  - Message timestamps
  - Message status (sent/delivered)
  - Typing indicators

✅ **UI/UX**
  - Material Design 3 interface
  - Light and dark themes
  - Smooth animations
  - Responsive layout
  - Error handling with user feedback
  - Loading states

## Project Structure

```
app/src/
├── main/
│   ├── kotlin/com/chatapp/
│   │   ├── api/
│   │   │   ├── ApiService.kt       # API interface
│   │   │   └── RetrofitClient.kt   # Retrofit setup
│   │   ├── data/
│   │   │   ├── ChatRepository.kt   # Business logic
│   │   │   ├── local/
│   │   │   │   └── SessionManager.kt
│   │   │   └── models/
│   │   │       └── Models.kt       # Data classes
│   │   ├── ui/
│   │   │   ├── components/
│   │   │   │   └── Components.kt   # Reusable UI components
│   │   │   ├── screens/
│   │   │   │   ├── AuthScreens.kt  # Login & Signup
│   │   │   │   └── ChatScreens.kt  # Chat UI
│   │   │   ├── theme/
│   │   │   │   ├── Color.kt
│   │   │   │   ├── Typography.kt
│   │   │   │   └── Theme.kt
│   │   │   └── viewmodel/
│   │   │       ├── LoginViewModel.kt
│   │   │       ├── ChatListViewModel.kt
│   │   │       └── ChatDetailViewModel.kt
│   │   ├── utils/
│   │   │   ├── Constants.kt
│   │   │   ├── DateUtils.kt
│   │   │   └── FileUtils.kt
│   │   ├── ChatApplication.kt      # Hilt app class
│   │   └── MainActivity.kt         # Entry point
│   └── res/
│       └── values/
│           ├── strings.xml
│           └── styles.xml
└── AndroidManifest.xml
```

## Setup Instructions

### 1. Prerequisites
- Android Studio Giraffe or later
- JDK 11+
- Android SDK 34 (API level 34)
- Kotlin 1.9+

### 2. Configuration
Edit `Constants.kt` with your server details:
```kotlin
const val BASE_URL = "http://YOUR_IP:8000/"
```

For emulator: `http://10.0.2.2:8000/`
For physical device: `http://YOUR_DEVICE_IP:8000/`

### 3. Build & Run
```bash
./gradlew build
./gradlew installDebug  # For emulator/device
```

Or use Android Studio's "Run" button.

### 4. Permissions
The app requires:
- INTERNET - API communication
- READ_EXTERNAL_STORAGE - File uploads
- WRITE_EXTERNAL_STORAGE - File downloads
- CAMERA - Optional: for photo capture

## API Endpoints Used

All endpoints match your FastAPI backend:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /signup | Create new account |
| POST | /login | User login |
| POST | /logout/{username} | User logout |
| POST | /heartbeat/{username} | Keep alive |
| GET | /search_users/{query} | Search users |
| GET | /online_status/{username} | Get user status |
| GET | /all_online_status | Get all statuses |
| POST | /send_message | Send message |
| GET | /get_messages/{user1}/{user2} | Get conversation |
| GET | /get_conversations/{username} | List all conversations |
| PUT | /edit_message/{id} | Edit message |
| DELETE | /delete_message/{id}/{type} | Delete message |
| POST | /upload_chat_file | Upload file |
| GET | /download_chat_file/{filename} | Download file |

## Compatibility

- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 15)
- **Languages**: Kotlin
- **Architecture**: MVVM with Repository pattern

## Testing

### Test Accounts
Create accounts in the chat app - they sync with your FastAPI backend automatically.

### Manual Testing Checklist
- [ ] Signup works
- [ ] Login works
- [ ] Session persists after app close
- [ ] Can search and find users
- [ ] Can send/receive messages
- [ ] Online status updates
- [ ] File upload works (test with image)
- [ ] Message editing works
- [ ] Message deletion works
- [ ] Dark mode works
- [ ] Logout works

## Troubleshooting

### "Connection refused" error
- Check if backend server is running
- Verify BASE_URL in Constants.kt
- For emulator, use `10.0.2.2:8000`
- For device, use your PC's local IP

### File upload fails
- Check file size < 200MB
- Check WRITE_EXTERNAL_STORAGE permission
- Check backend storage directory exists

### Messages don't refresh
- Check network connectivity
- Verify API responses in Retrofit logs
- Check backend is running

## Future Enhancements

- [ ] Push notifications
- [ ] Message encryption
- [ ] Group chats
- [ ] Voice messages
- [ ] Video calls
- [ ] User blocking
- [ ] Message reactions
  - [ ] Cloud backup
- [ ] Firebase integration
- [ ] SQLCipher for encrypted database
- [ ] SSL certificate pinning

## License

MIT License - Free to use and modify
