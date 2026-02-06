package com.chatapp.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.chatapp.api.RetrofitClient
import com.chatapp.data.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AuthViewModel : ViewModel() {
    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private val _currentUser = MutableStateFlow("")
    val currentUser: StateFlow<String> = _currentUser.asStateFlow()

    private val _currentToken = MutableStateFlow("")
    val currentToken: StateFlow<String> = _currentToken.asStateFlow()

    private val _isAdmin = MutableStateFlow(false)
    val isAdmin: StateFlow<Boolean> = _isAdmin.asStateFlow()

    fun login(username: String, password: String) {
        viewModelScope.launch {
            try {
                _authState.value = AuthState.Loading
                val response = RetrofitClient.apiService.login(
                    LoginRequest(username, password)
                )
                _currentUser.value = response.username
                _currentToken.value = response.token
                _isAdmin.value = response.is_admin
                _authState.value = AuthState.Success(response.message)
            } catch (e: Exception) {
                _authState.value = AuthState.Error(e.message ?: "Login failed")
            }
        }
    }

    fun signup(username: String, password: String) {
        viewModelScope.launch {
            try {
                _authState.value = AuthState.Loading
                val response = RetrofitClient.apiService.signup(
                    SignupRequest(username, password)
                )
                _currentUser.value = response.username
                _currentToken.value = response.token
                _isAdmin.value = response.is_admin
                _authState.value = AuthState.Success(response.message)
            } catch (e: Exception) {
                _authState.value = AuthState.Error(e.message ?: "Signup failed")
            }
        }
    }

    fun logout(username: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.logout(username)
                _currentUser.value = ""
                _currentToken.value = ""
                _isAdmin.value = false
                _authState.value = AuthState.Idle
            } catch (e: Exception) {
                // Logout locally even if request fails
                _currentUser.value = ""
                _currentToken.value = ""
                _isAdmin.value = false
                _authState.value = AuthState.Idle
            }
        }
    }

    fun startHeartbeat(username: String) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.heartbeat(username)
            } catch (e: Exception) {
                // Heartbeat failed, user might be banned
                _authState.value = AuthState.Error("Connection lost or banned")
            }
        }
    }

    fun setUserData(username: String, token: String, isAdmin: Boolean) {
        _currentUser.value = username
        _currentToken.value = token
        _isAdmin.value = isAdmin
        _authState.value = AuthState.Idle
    }
}

sealed class AuthState {
    object Idle : AuthState()
    object Loading : AuthState()
    data class Success(val message: String) : AuthState()
    data class Error(val message: String) : AuthState()
}
