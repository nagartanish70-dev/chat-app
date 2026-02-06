package com.chatapp.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import com.google.gson.Gson
import com.google.gson.GsonBuilder

object RetrofitClient {
    private const val BASE_URL = "http://10.0.2.2:8000/" // For Android emulator localhost

    private val gson: Gson = GsonBuilder()
        .setLenient()
        .create()

    val apiService: ChatApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
            .create(ChatApiService::class.java)
    }
}

object Constants {
    const val API_BASE_URL = "http://10.0.2.2:8000/" // For Android emulator
    const val FCM_HEARTBEAT_INTERVAL = 10000L // 10 seconds
    const val MESSAGE_REFRESH_INTERVAL = 2000L // 2 seconds
    const val STATUS_REFRESH_INTERVAL = 5000L // 5 seconds
    const val MAX_FILE_SIZE = 200 * 1024 * 1024L // 200 MB
    const val MESSAGE_PAGE_SIZE = 50
    const val CONVERSATION_PAGE_SIZE = 25
}
