package com.chatapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chatapp.api.RetrofitClient
import com.chatapp.data.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ChatDetailViewModel : ViewModel() {
    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    private val _currentChatUser = MutableStateFlow("")
    val currentChatUser: StateFlow<String> = _currentChatUser.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _error = MutableStateFlow("")
    val error: StateFlow<String> = _error.asStateFlow()

    private val _messageText = MutableStateFlow("")
    val messageText: StateFlow<String> = _messageText.asStateFlow()

    private val _selectedFile = MutableStateFlow<FileData?>(null)
    val selectedFile: StateFlow<FileData?> = _selectedFile.asStateFlow()

    private val _isRecording = MutableStateFlow(false)
    val isRecording: StateFlow<Boolean> = _isRecording.asStateFlow()

    fun setChatUser(username: String) {
        _currentChatUser.value = username
        loadMessages(username)
    }

    fun setMessageText(text: String) {
        _messageText.value = text
    }

    fun setSelectedFile(file: FileData?) {
        _selectedFile.value = file
    }

    fun setRecording(recording: Boolean) {
        _isRecording.value = recording
    }

    fun loadMessages(otherUser: String, currentUser: String = _currentChatUser.value) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val response = RetrofitClient.apiService.getMessages(currentUser, otherUser)
                _messages.value = response.messages.sortedBy { it.timestamp }
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to load messages"
                _isLoading.value = false
            }
        }
    }

    fun sendMessage(fromUser: String, toUser: String, message: String, fileData: FileData? = null) {
        viewModelScope.launch {
            try {
                _isLoading.value = true
                val request = SendMessageRequest(
                    from_user = fromUser,
                    to_user = toUser,
                    message = message,
                    file_url = fileData?.url,
                    file_name = fileData?.name,
                    file_type = fileData?.type
                )
                RetrofitClient.apiService.sendMessage(request)
                _messageText.value = ""
                _selectedFile.value = null
                loadMessages(toUser, fromUser)
                _isLoading.value = false
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to send message"
                _isLoading.value = false
            }
        }
    }

    fun editMessage(messageId: String, newText: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.editMessage(
                    messageId,
                    EditMessageRequest(newText)
                )
                loadMessages(_currentChatUser.value)
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to edit message"
            }
        }
    }

    fun deleteMessage(messageId: String, deleteType: String, currentUser: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.deleteMessage(
                    messageId,
                    deleteType,
                    DeleteMessageRequest(currentUser)
                )
                loadMessages(_currentChatUser.value)
            } catch (e: Exception) {
                _error.value = e.message ?: "Failed to delete message"
            }
        }
    }

    fun uploadFile(fileName: String, filePath: String): FileData? {
        // This would handle file upload in a real app
        // For now, returning a mock response
        return FileData(
            url = "/chat_files/$fileName",
            name = fileName,
            type = getFileType(fileName)
        )
    }

    private fun getFileType(fileName: String): String {
        return when {
            fileName.endsWith(".jpg") || fileName.endsWith(".jpeg") || fileName.endsWith(".png") -> "image"
            fileName.endsWith(".mp4") || fileName.endsWith(".avi") -> "video"
            fileName.endsWith(".mp3") || fileName.endsWith(".wav") || fileName.endsWith(".webm") -> "audio"
            else -> "file"
        }
    }

    fun clearError() {
        _error.value = ""
    }
}

data class FileData(
    val url: String,
    val name: String,
    val type: String
)
