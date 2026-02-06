package com.chatapp.data

import java.io.Serializable

// Authentication
data class LoginRequest(val username: String, val password: String)
data class SignupRequest(val username: String, val password: String)
data class AuthResponse(
    val message: String,
    val username: String,
    val token: String,
    val is_admin: Boolean = false
)

// User
data class User(
    val username: String,
    val password: String,
    val is_banned: Boolean = false
)

// Message
data class Message(
    val id: String = "",
    val from: String = "",
    val to: String = "",
    val message: String = "",
    val timestamp: String = "",
    val file_url: String? = null,
    val file_name: String? = null,
    val file_type: String? = null,
    val edited: Boolean = false,
    val deleted_for: List<String> = emptyList()
) : Serializable

// Send Message Request
data class SendMessageRequest(
    val from_user: String,
    val to_user: String,
    val message: String = "",
    val file_url: String? = null,
    val file_name: String? = null,
    val file_type: String? = null
)

// Edit Message Request
data class EditMessageRequest(val message: String)

// Delete Message Request
data class DeleteMessageRequest(val username: String)

// File Upload Response
data class FileUploadResponse(
    val file_url: String,
    val file_name: String,
    val file_type: String
)

// Search Users Response
data class SearchResponse(val users: List<String>)

// Conversations Response
data class ConversationsResponse(val conversations: List<String>)

// Messages Response
data class MessagesResponse(val messages: List<Message>)

// Online Status
data class OnlineStatus(
    val status: String
)

data class AllOnlineStatusResponse(
    val statuses: Map<String, OnlineStatus>
) : Serializable

// Admin Responses
data class AdminUser(
    val username: String,
    val password: String,
    val password_hash: String,
    val is_banned: Boolean
)

data class AdminUsersResponse(val users: List<AdminUser>)

data class AdminConversation(
    val users: List<String>,
    val message_count: Int
)

data class AdminConversationsResponse(val conversations: List<AdminConversation>)

// Ban/Unban Request
data class BanRequest(val username: String)

// Change Password Request
data class ChangePasswordRequest(
    val username: String,
    val new_password: String
)

// App State
data class AppState(
    val isLoggedIn: Boolean = false,
    val currentUser: String = "",
    val currentToken: String = "",
    val isAdmin: Boolean = false
)

// Chat State
data class ChatState(
    val currentChatUser: String? = null,
    val messages: List<Message> = emptyList(),
    val conversations: List<String> = emptyList(),
    val onlineStatuses: Map<String, String> = emptyMap()
)
