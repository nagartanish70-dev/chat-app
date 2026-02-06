# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# signingConfig and minifyEnabled properties in build.gradle.kts.

-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Retrofit
-keepclasseswithmembers class ** {
    @retrofit2.http.* <methods>;
}

# Gson
-keepclassmembers class ** {
    @com.google.gson.annotations.SerializedName <fields>;
}

# Hilt
-keepclasseswithmembers class * {
    @javax.inject <methods>;
}

# Coroutines
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}
