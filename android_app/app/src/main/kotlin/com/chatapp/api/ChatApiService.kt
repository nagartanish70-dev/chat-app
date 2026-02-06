package com.chatapp.api

import com.chatapp.data.*
import retrofit2.http.*
import okhttp3.MultipartBody
import okhttp3.RequestBody

interface ChatApiService {
    // Authentication
    @POST("/signup")
    suspend fun signup(@Body request: SignupRequest): AuthResponse

    @POST("/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("/logout/{username}")
    suspend fun logout(@Path("username") username: String)

    @POST("/heartbeat/{username}")
    suspend fun heartbeat(@Path("username") username: String)

    // User Management
    @GET("/search_users/{query}")
    suspend fun searchUsers(@Path("query") query: String): SearchResponse

    @GET("/check_ban_status/{username}")
    suspend fun checkBanStatus(@Path("username") username: String)

    // Messages
    @POST("/send_message")
    suspend fun sendMessage(@Body request: SendMessageRequest): Message

    @GET("/get_messages/{user1}/{user2}")
    suspend fun getMessages(
        @Path("user1") user1: String,
        @Path("user2") user2: String
    ): MessagesResponse

    @GET("/get_conversations/{username}")
    suspend fun getConversations(@Path("username") username: String): ConversationsResponse

    @PUT("/edit_message/{message_id}")
    suspend fun editMessage(
        @Path("message_id") messageId: String,
        @Body request: EditMessageRequest
    ): Message

    @DELETE("/delete_message/{message_id}/{delete_type}")
    suspend fun deleteMessage(
        @Path("message_id") messageId: String,
        @Path("delete_type") deleteType: String,
        @Body request: DeleteMessageRequest
    )

    // File Operations
    @Multipart
    @POST("/upload_chat_file")
    suspend fun uploadChatFile(
        @Part file: MultipartBody.Part
    ): FileUploadResponse

    @GET("/download_chat_file/{filename}")
    suspend fun downloadChatFile(@Path("filename") filename: String)

    // Online Status
    @GET("/online_status/{username}")
    suspend fun getOnlineStatus(@Path("username") username: String): OnlineStatus

    @GET("/all_online_status")
    suspend fun getAllOnlineStatus(): Map<String, OnlineStatus>

    // Admin Endpoints
    @GET("/admin/all_users")
    suspend fun adminGetAllUsers(): AdminUsersResponse

    @GET("/admin/all_conversations")
    suspend fun adminGetAllConversations(): AdminConversationsResponse

    @GET("/admin/messages/{user1}/{user2}")
    suspend fun adminGetMessages(
        @Path("user1") user1: String,
        @Path("user2") user2: String
    ): MessagesResponse

    @GET("/admin/banned_users")
    suspend fun adminGetBannedUsers(): AdminUsersResponse

    @POST("/admin/ban_user")
    suspend fun adminBanUser(@Body request: BanRequest)

    @POST("/admin/unban_user")
    suspend fun adminUnbanUser(@Body request: BanRequest)

    @POST("/admin/change_password")
    suspend fun adminChangePassword(@Body request: ChangePasswordRequest)
}
