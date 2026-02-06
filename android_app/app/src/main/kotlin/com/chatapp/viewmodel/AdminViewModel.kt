package com.chatapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chatapp.api.RetrofitClient
import com.chatapp.data.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AdminViewModel : ViewModel() {
    private val _adminUsers = MutableStateFlow<List<AdminUser>>(emptyList())
    val adminUsers: StateFlow<List<AdminUser>> = _adminUsers.asStateFlow()

    private val _adminConversations = MutableStateFlow<List<AdminConversation>>(emptyList())
    val adminConversations: StateFlow<List<AdminConversation>> = _adminConversations.asStateFlow()

    private val _adminMessages = MutableStateFlow<List<Message>>(emptyList())
    val adminMessages: StateFlow<List<Message>> = _adminMessages.asStateFlow()

    private val _currentAdminTab = MutableStateFlow("users")
    val currentAdminTab: StateFlow<String> = _currentAdminTab.asStateFlow()

    private val _currentAdminChatPair = MutableStateFlow<Pair<String, String>?>(null)
    val currentAdminChatPair: StateFlow<Pair<String, String>?> = _currentAdminChatPair.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow("")
    val error: StateFlow<String> = _error.asStateFlow()

    fun loadAdminUsers() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response = RetrofitClient.apiService.adminGetAllUsers()
                _adminUsers.value = response.users
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load users"
                _isLoading.value = false
            }
        }
    }

    fun loadAdminConversations() {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response = RetrofitClient.apiService.adminGetAllConversations()
                _adminConversations.value = response.conversations
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load conversations"
                _isLoading.value = false
            }
        }
    }

    fun loadAdminMessages(user1: String, user2: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response = RetrofitClient.apiService.adminGetMessages(user1, user2)
                _adminMessages.value = response.messages.sortedBy { it.timestamp }
                _currentAdminChatPair.value = Pair(user1, user2)
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load messages"
                _isLoading.value = false
            }
        }
    }

    fun banUser(username: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.adminBanUser(BanRequest(username))
                loadAdminUsers()
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to ban user"
            }
        }
    }

    fun unbanUser(username: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.adminUnbanUser(BanRequest(username))
                loadAdminUsers()
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to unban user"
            }
        }
    }

    fun changePassword(username: String, newPassword: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.adminChangePassword(
                    ChangePasswordRequest(username, newPassword)
                )
                loadAdminUsers()
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to change password"
            }
        }
    }

    fun switchTab(tab: String) {
        _currentAdminTab.value = tab
        when (tab) {
            "users" -> loadAdminUsers()
            "chats" -> loadAdminConversations()
        }
    }

    fun clearAdminChat() {
        _currentAdminChatPair.value = null
        _adminMessages.value = emptyList()
    }

    fun clearError() {
        _error.value = ""
    }
}
