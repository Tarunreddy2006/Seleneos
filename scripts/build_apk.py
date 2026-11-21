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

# 5. Write MainActivity.java (with dynamic server connection dialog & resilient fallback)
main_activity = """package com.dailyintelligence.app;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.webkit.WebChromeClient;
import android.view.KeyEvent;
import android.view.Window;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Toast;

public class MainActivity extends Activity {
    private WebView webView;
    private SharedPreferences prefs;
    private static final String PREF_KEY_SERVER = "server_url";
    private static final String DEFAULT_SERVER = "http://127.0.0.1:8000";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.activity_main);

        prefs = getSharedPreferences("daily_intel_prefs", MODE_PRIVATE);

        webView = findViewById(R.id.webview);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom(true);
        settings.setBuiltInZoomControls(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith("app://configure-server")) {
                    showServerConfigDialog();
                    return true;
                }
                view.loadUrl(url);
                return true;
            }

            @Override
            public void onReceivedError(WebView view, int errorCode, String description, String failingUrl) {
                showErrorPage(failingUrl, description);
            }
        });

        loadCurrentServer();
    }

    private String getServerUrl() {
        return prefs.getString(PREF_KEY_SERVER, DEFAULT_SERVER);
    }

    private void loadCurrentServer() {
        String url = getServerUrl();
        webView.loadUrl(url);
    }

    private void showErrorPage(String failingUrl, String errorMsg) {
        String server = getServerUrl();
        String html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            + "<style>body{font-family:-apple-system,sans-serif;background:#0f172a;color:#f8fafc;padding:32px 20px;text-align:center;}"
            + ".card{background:#1e293b;border-radius:12px;padding:24px;border:1px solid #334155;margin-top:20px;box-shadow:0 4px 6px rgba(0,0,0,0.3);}"
            + "h2{font-size:1.3rem;margin-bottom:8px;color:#60a5fa;}p{color:#94a3b8;font-size:0.95rem;line-height:1.5;}"
            + "code{background:#0f172a;padding:3px 8px;border-radius:4px;color:#38bdf8;font-size:0.9rem;}"
            + "button{background:#2563eb;color:#fff;border:none;padding:10px 18px;border-radius:6px;font-size:0.92rem;font-weight:600;margin:8px 4px;cursor:pointer;}"
            + ".btn-sec{background:#334155;color:#e2e8f0;}"
            + "</style></head><body>"
            + "<div class='card'>"
            + "<h2>Daily Intelligence</h2>"
            + "<p>Waiting to connect to backend server at:<br><br><code>" + server + "</code></p>"
            + "<p style='font-size:0.85rem;color:#64748b;margin-top:14px;'>Run your backend on phone (127.0.0.1:8000) or connect to your laptop over Wi-Fi.</p>"
            + "<div style='margin-top:24px;display:flex;justify-content:center;gap:12px;'>"
            + "<button onclick='location.reload()'>Retry</button>"
            + "<a href='app://configure-server' style='background:#334155;color:#e2e8f0;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:600;font-size:0.92rem;'>Change Server IP</a>"
            + "</div></div></body></html>";
        webView.loadDataWithBaseURL(null, html, "text/html", "utf-8", null);
    }

    private void showServerConfigDialog() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Server Connection Settings");
        builder.setMessage("Enter the URL of your Daily Intelligence backend server:");

        final EditText input = new EditText(this);
        input.setText(getServerUrl());
        input.setSelection(input.getText().length());

        LinearLayout layout = new LinearLayout(this);
        layout.setPadding(40, 20, 40, 10);
        layout.addView(input);
        builder.setView(layout);

        builder.setPositiveButton("Connect", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                String newUrl = input.getText().toString().trim();
                if (!newUrl.startsWith("http://") && !newUrl.startsWith("https://")) {
                    newUrl = "http://" + newUrl;
                }
                prefs.edit().putString(PREF_KEY_SERVER, newUrl).apply();
                Toast.makeText(MainActivity.this, "Connecting to " + newUrl, Toast.LENGTH_SHORT).show();
                loadCurrentServer();
            }
        });

        builder.setNeutralButton("Reset (127.0.0.1)", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                prefs.edit().putString(PREF_KEY_SERVER, DEFAULT_SERVER).apply();
                loadCurrentServer();
            }
        });

        builder.setNegativeButton("Cancel", null);
        builder.show();
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
