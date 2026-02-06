# Android Chat App - Setup & Structure

This directory contains a complete Android Chat Application in Kotlin with Jetpack Compose.

## Project Structure

```
ChatAppAndroid/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── kotlin/com/chatapp/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── api/
│   │   │   │   │   ├── ApiService.kt
│   │   │   │   │   └── RetrofitClient.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── models/
│   │   │   │   │   │   ├── User.kt
│   │   │   │   │   │   ├── Message.kt
│   │   │   │   │   │   └── ApiResponses.kt
│   │   │   │   │   ├── repository/
│   │   │   │   │   │   └── ChatRepository.kt
│   │   │   │   │   └── local/
│   │   │   │   │       ├── AppDatabase.kt
│   │   │   │   │       └── SessionManager.kt
│   │   │   │   ├── ui/
│   │   │   │   │   ├── screens/
│   │   │   │   │   │   ├── LoginScreen.kt
│   │   │   │   │   │   ├── SignupScreen.kt
│   │   │   │   │   │   ├── ChatListScreen.kt
│   │   │   │   │   │   ├── ChatDetailScreen.kt
│   │   │   │   │   │   └── UserProfileScreen.kt
│   │   │   │   │   ├── components/
│   │   │   │   │   │   ├── ChatMessage.kt
│   │   │   │   │   │   ├── UserItem.kt
│   │   │   │   │   │   ├── FileUploadDialog.kt
│   │   │   │   │   │   └── OnlineStatusIndicator.kt
│   │   │   │   │   ├── theme/
│   │   │   │   │   │   ├── Color.kt
│   │   │   │   │   │   ├── Typography.kt
│   │   │   │   │   │   └── Theme.kt
│   │   │   │   │   └── viewmodel/
│   │   │   │   │       ├── LoginViewModel.kt
│   │   │   │   │       ├── ChatViewModel.kt
│   │   │   │   │       └── ChatDetailViewModel.kt
│   │   │   │   └── utils/
│   │   │   │       ├── FileUtils.kt
│   │   │   │       ├── DateUtils.kt
│   │   │   │       └── Constants.kt
│   │   │   └── res/
│   │   │       ├── values/strings.xml
│   │   │       └── mipmap/ic_launcher.xml
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── build.gradle.kts
└── settings.gradle.kts
```

## Features Implemented

✅ User Registration & Login  
✅ Real-time Messaging  
✅ File Sharing (up to 200MB - images, videos, files)  
✅ Online/Offline Status  
✅ Session Persistence (stays logged in)  
✅ Message Search  
✅ User Search  
✅ Edit & Delete Messages  
✅ Conversation History  
✅ Modern Material Design 3 UI  
✅ Dark Mode Support  
✅ Offline Support with Local Storage  

## Setup Instructions

### 1. Prerequisites
- Android Studio (latest version)
- Android SDK 24+ (API level 24)
- JDK 11+
- Kotlin 1.9+

### 2. Create New Android Project
1. Open Android Studio
2. Create New Project → Empty Activity
3. Select Kotlin language
4. Target API 34 (min API 24)
5. Replace all files with the ones provided below

### 3. Configure Backend URL
Edit `app/src/main/kotlin/com/chatapp/utils/Constants.kt`:
```kotlin
const val BASE_URL = "http://YOUR_SERVER_IP:8000/"  // Update with your server IP
```

### 4. Build & Run
```bash
# In Android Studio Terminal:
./gradlew build
./gradlew installDebug  # For emulator
```

## API Endpoints Used
All endpoints use the same FastAPI backend:
- POST /signup - User registration
- POST /login - User login
- GET /search_users/{query} - Search users
- POST /send_message - Send message
- GET /get_messages/{user1}/{user2} - Get conversation
- GET /get_conversations/{username} - Get all conversations
- POST /upload_chat_file - Upload file
- GET /download_chat_file/{filename} - Download file
- POST /heartbeat/{username} - Keep alive
- POST /logout/{username} - Logout
- GET /all_online_status - Online status

## Permissions Required
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.CAMERA" />
```

## Dependencies
- Jetpack Compose for UI
- Retrofit 2 for API calls
- Room for local database
- Coroutines for async operations
- Hilt for dependency injection
- Datastore for session persistence
- Coil/Glide for image loading

## Testing
The app is compatible with:
- Android 7.0+ (API 24)
- Latest Android 15 (API 35)
- All modern Android devices and emulators

## Notes
- Session tokens stored securely in encrypted Datastore
- File uploads streamed to prevent memory issues
- Real-time message updates with polling
- Automatic online status updates every 30 seconds
- Supports light/dark theme switching
