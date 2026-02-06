package com.chatapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chatapp.api.RetrofitClient
import com.chatapp.data.SearchResponse
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ChatListViewModel : ViewModel() {
    private val _conversations = MutableStateFlow<List<String>>(emptyList())
    val conversations: StateFlow<List<String>> = _conversations.asStateFlow()

    private val _searchResults = MutableStateFlow<List<String>>(emptyList())
    val searchResults: StateFlow<List<String>> = _searchResults.asStateFlow()

    private val _onlineStatuses = MutableStateFlow<Map<String, String>>(emptyMap())
    val onlineStatuses: StateFlow<Map<String, String>> = _onlineStatuses.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow("")
    val error: StateFlow<String> = _error.asStateFlow()

    fun loadConversations(username: String) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response = RetrofitClient.apiService.getConversations(username)
                _conversations.value = response.conversations
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load conversations"
                _isLoading.value = false
            }
        }
    }

    fun searchUsers(query: String) {
        viewModelScope.launch {
            try {
                if (query.isEmpty()) {
                    _searchResults.value = emptyList()
                    return@launch
                }
                val response = RetrofitClient.apiService.searchUsers(query)
                _searchResults.value = response.users
            } catch (e: Exception) {
                _error.value = e.message ?: "Search failed"
            }
        }
    }

    fun loadOnlineStatuses() {
        viewModelScope.launch {
            try {
                val statuses = RetrofitClient.apiService.getAllOnlineStatus()
                _onlineStatuses.value = statuses.mapValues { (_, v) -> v.status }
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load statuses"
            }
        }
    }

    fun clearSearch() {
        _searchResults.value = emptyList()
    }

    fun clearError() {
        _error.value = ""
    }

    fun isUserOnline(username: String): Boolean {
        return _onlineStatuses.value[username] == "online"
    }
}
