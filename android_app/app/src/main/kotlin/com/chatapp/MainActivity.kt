package com.chatapp

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.*
import androidx.activity.ComponentActivity

class MainActivity : ComponentActivity() {
    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val webView = WebView(this)
        
        // Enable cookies for session management
        CookieManager.getInstance().apply {
            setAcceptCookie(true)
            setAcceptThirdPartyCookies(webView, true)
        }
        
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            
            // Enable debugging
            WebView.setWebContentsDebuggingEnabled(true)
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                android.util.Log.e("WebView", "Error: ${error?.description}")
            }
            
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                // Override fetch to redirect localhost:8000 to 10.0.2.2:8000
                view?.evaluateJavascript(
                    """
                    (function() {
                        const originalFetch = window.fetch;
                        window.fetch = function(url, options) {
                            if (typeof url === 'string' && url.includes('localhost:8000')) {
                                url = url.replace('localhost:8000', '10.0.2.2:8000');
                            }
                            return originalFetch(url, options);
                        };
                    })();
                    """.trimIndent(),
                    null
                )
            }
        }
        
        webView.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                android.util.Log.d("WebView", "${consoleMessage?.message()}")
                return true
            }
        }
        
        // Load your actual website from localhost
        webView.loadUrl("http://10.0.2.2:8080/chat.html")
        
        setContentView(webView)
    }
}
