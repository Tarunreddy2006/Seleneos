import os
import sys
import shutil
import subprocess
import zipfile

# Tool paths
JDK_BIN = r"C:\Program Files\Java\jdk-17.0.18\bin"
SDK_DIR = r"C:\Users\THARUN. R\AppData\Local\Android\Sdk"
BUILD_TOOLS = os.path.join(SDK_DIR, "build-tools", "34.0.0")
ANDROID_JAR = os.path.join(SDK_DIR, "platforms", "android-34", "android.jar")

AAPT2 = os.path.join(BUILD_TOOLS, "aapt2.exe")
D8 = os.path.join(BUILD_TOOLS, "d8.bat")
ZIPALIGN = os.path.join(BUILD_TOOLS, "zipalign.exe")
APKSIGNER = os.path.join(BUILD_TOOLS, "apksigner.bat")

JAVAC = os.path.join(JDK_BIN, "javac.exe")
KEYTOOL = os.path.join(JDK_BIN, "keytool.exe")

BUILD_DIR = os.path.abspath("android_apk_build")
OUTPUT_APK = os.path.abspath("DailyIntelligence.apk")

env = os.environ.copy()
env["JAVA_HOME"] = r"C:\Program Files\Java\jdk-17.0.18"
env["PATH"] = rf"{JDK_BIN};{BUILD_TOOLS};{env.get('PATH', '')}"

print(f"=== Daily Intelligence APK Builder ===")
print(f"Building in: {BUILD_DIR}")
print(f"Target Output: {OUTPUT_APK}")

# Clean build directory
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(BUILD_DIR, exist_ok=True)

res_dir = os.path.join(BUILD_DIR, "res")
values_dir = os.path.join(res_dir, "values")
layout_dir = os.path.join(res_dir, "layout")
drawable_dir = os.path.join(res_dir, "drawable")
assets_dir = os.path.join(BUILD_DIR, "assets")
src_dir = os.path.join(BUILD_DIR, "src", "com", "dailyintelligence", "app")
bin_dir = os.path.join(BUILD_DIR, "bin")

for d in [values_dir, layout_dir, drawable_dir, assets_dir, src_dir, bin_dir]:
    os.makedirs(d, exist_ok=True)

# 1. Copy Frontend Assets
frontend_src = os.path.abspath(os.path.join("app", "frontend"))
for item in os.listdir(frontend_src):
    s = os.path.join(frontend_src, item)
    d = os.path.join(assets_dir, item)
    if os.path.isdir(s):
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)

# 2. Write AndroidManifest.xml
manifest_content = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.dailyintelligence.app"
    android:versionCode="1"
    android:versionName="1.0.0">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:label="@string/app_name"
        android:theme="@android:style/Theme.Material.Light.NoActionBar"
        android:usesCleartextTraffic="true"
        android:hardwareAccelerated="true">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""
with open(os.path.join(BUILD_DIR, "AndroidManifest.xml"), "w", encoding="utf-8") as f:
    f.write(manifest_content)

# 3. Write strings.xml
strings_content = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Daily Intelligence</string>
</resources>
"""
with open(os.path.join(values_dir, "strings.xml"), "w", encoding="utf-8") as f:
    f.write(strings_content)

# 4. Write activity_main.xml layout
layout_content = """<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

</RelativeLayout>
"""
with open(os.path.join(layout_dir, "activity_main.xml"), "w", encoding="utf-8") as f:
    f.write(layout_content)

# 5. Write MainActivity.java (Embedded Standalone Engine with Native Bridge)
main_activity = """package com.dailyintelligence.app;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.view.KeyEvent;
import android.view.Window;
import android.widget.Toast;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class MainActivity extends Activity {
    private WebView webView;

    public class WebAppInterface {
        @JavascriptInterface
        public boolean isNativeApp() {
            return true;
        }

        @JavascriptInterface
        public void showToast(final String message) {
            runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    Toast.makeText(MainActivity.this, message, Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public String fetchHttp(String urlString) {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(urlString);
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 14; Mobile) DailyIntelligence/1.0");
                conn.setRequestProperty("Accept", "application/rss+xml, application/xml, text/xml, */*");
                conn.setConnectTimeout(12000);
                conn.setReadTimeout(15000);
                conn.setInstanceFollowRedirects(true);

                int code = conn.getResponseCode();
                if (code >= 200 && code < 400) {
                    BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream(), "UTF-8"));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = in.readLine()) != null) {
                        response.append(line).append("\\n");
                    }
                    in.close();
                    return response.toString();
                }
            } catch (Exception e) {
                e.printStackTrace();
            } finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
            return null;
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith("http://") || url.startsWith("https://")) {
                    try {
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    } catch (Exception e) {
                        return false;
                    }
                }
                view.loadUrl(url);
                return true;
            }
        });

        webView.addJavascriptInterface(new WebAppInterface(), "AndroidBridge");
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if ((keyCode == KeyEvent.KEYCODE_BACK) && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
"""
with open(os.path.join(src_dir, "MainActivity.java"), "w", encoding="utf-8") as f:
    f.write(main_activity)

print("[1/6] Compiling resources with AAPT2...")
flat_res = os.path.join(BUILD_DIR, "compiled_res.zip")
cmd_compile = [
    AAPT2, "compile",
    "--dir", res_dir,
    "-o", flat_res
]
subprocess.run(cmd_compile, check=True, env=env)

print("[2/6] Linking resources and generating R.java...")
gen_dir = os.path.join(BUILD_DIR, "gen")
os.makedirs(gen_dir, exist_ok=True)
cmd_link = [
    AAPT2, "link",
    "-I", ANDROID_JAR,
    "--manifest", os.path.join(BUILD_DIR, "AndroidManifest.xml"),
    "--java", gen_dir,
    "-o", os.path.join(BUILD_DIR, "app_res.apk"),
    "-A", assets_dir,
    "--auto-add-overlay",
    flat_res
]
subprocess.run(cmd_link, check=True, env=env)

print("[3/6] Compiling Java classes with javac...")
r_java = os.path.join(gen_dir, "com", "dailyintelligence", "app", "R.java")
java_src = os.path.join(src_dir, "MainActivity.java")

cmd_javac = [
    JAVAC,
    "-cp", ANDROID_JAR,
    "-source", "1.8",
    "-target", "1.8",
    "-d", bin_dir,
    r_java,
    java_src
]
subprocess.run(cmd_javac, check=True, env=env)

print("[4/6] Converting Java bytecode to Dalvik dex (d8)...")
class_files = []
for root, dirs, files in os.walk(bin_dir):
    for f in files:
        if f.endswith(".class"):
            class_files.append(os.path.join(root, f))

cmd_d8 = [
    D8,
    "--lib", ANDROID_JAR,
    "--output", BUILD_DIR
] + class_files
subprocess.run(cmd_d8, check=True, env=env)

print("[5/6] Assembling APK...")
unaligned_apk = os.path.join(BUILD_DIR, "unaligned.apk")
shutil.copy2(os.path.join(BUILD_DIR, "app_res.apk"), unaligned_apk)

with zipfile.ZipFile(unaligned_apk, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(BUILD_DIR, "classes.dex"), "classes.dex")

aligned_apk = os.path.join(BUILD_DIR, "aligned.apk")
if os.path.exists(aligned_apk):
    os.remove(aligned_apk)
cmd_zipalign = [
    ZIPALIGN, "-p", "-f", "4",
    unaligned_apk,
    aligned_apk
]
subprocess.run(cmd_zipalign, check=True, env=env)

print("[6/6] Generating keystore and signing APK...")
keystore_path = os.path.join(BUILD_DIR, "release.keystore")
if not os.path.exists(keystore_path):
    cmd_keytool = [
        KEYTOOL,
        "-genkeypair",
        "-v",
        "-keystore", keystore_path,
        "-alias", "daily_intel_key",
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-storepass", "android123",
        "-keypass", "android123",
        "-dname", "CN=DailyIntelligence, OU=Personal, O=Intelligence, L=Bengaluru, ST=Karnataka, C=IN"
    ]
    subprocess.run(cmd_keytool, check=True, env=env)

if os.path.exists(OUTPUT_APK):
    os.remove(OUTPUT_APK)
shutil.copy2(aligned_apk, OUTPUT_APK)

cmd_sign = [
    APKSIGNER, "sign",
    "--ks", keystore_path,
    "--ks-key-alias", "daily_intel_key",
    "--ks-pass", "pass:android123",
    "--key-pass", "pass:android123",
    OUTPUT_APK
]
subprocess.run(cmd_sign, check=True, env=env)

size_mb = os.path.getsize(OUTPUT_APK) / (1024 * 1024)
print(f"SUCCESS: Generated signed APK at: {OUTPUT_APK} ({size_mb:.2f} MB)")
