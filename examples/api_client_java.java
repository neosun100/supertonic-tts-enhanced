import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;
import org.json.JSONArray;

/**
 * Supertonic TTS - Java API Client Example
 * 调用 HTTP API 进行文本转语音的 Java 客户端示例
 * 
 * 依赖: org.json (JSON 库)
 * Maven: <dependency><groupId>org.json</groupId><artifactId>json</artifactId><version>20231013</version></dependency>
 * Gradle: implementation 'org.json:json:20231013'
 */
public class ApiClientJava {
    
    // API 配置
    private static final String API_BASE_URL = System.getenv().getOrDefault("API_URL", "http://localhost:8088");
    
    /**
     * 发送 HTTP GET 请求
     */
    private static JSONObject httpGet(String endpoint) throws IOException {
        URL url = new URL(API_BASE_URL + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.setRequestProperty("Accept", "application/json");
        
        int responseCode = conn.getResponseCode();
        if (responseCode != 200) {
            throw new IOException("HTTP " + responseCode + ": " + conn.getResponseMessage());
        }
        
        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();
        
        return new JSONObject(response.toString());
    }
    
    /**
     * 发送 HTTP POST 请求
     */
    private static JSONObject httpPost(String endpoint, JSONObject payload) throws IOException {
        URL url = new URL(API_BASE_URL + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json");
        conn.setRequestProperty("Accept", "application/json");
        conn.setDoOutput(true);
        
        // 发送请求体
        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = payload.toString().getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }
        
        int responseCode = conn.getResponseCode();
        if (responseCode != 200) {
            BufferedReader errorReader = new BufferedReader(new InputStreamReader(conn.getErrorStream()));
            StringBuilder errorResponse = new StringBuilder();
            String line;
            while ((line = errorReader.readLine()) != null) {
                errorResponse.append(line);
            }
            errorReader.close();
            throw new IOException("HTTP " + responseCode + ": " + errorResponse.toString());
        }
        
        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = in.readLine()) != null) {
            response.append(line);
        }
        in.close();
        
        return new JSONObject(response.toString());
    }
    
    /**
     * 下载文件
     */
    private static void downloadFile(String filename, String savePath) throws IOException {
        URL url = new URL(API_BASE_URL + "/" + filename);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        
        int responseCode = conn.getResponseCode();
        if (responseCode != 200) {
            throw new IOException("下载失败: HTTP " + responseCode);
        }
        
        try (InputStream in = conn.getInputStream();
             FileOutputStream out = new FileOutputStream(savePath)) {
            byte[] buffer = new byte[4096];
            int bytesRead;
            while ((bytesRead = in.read(buffer)) != -1) {
                out.write(buffer, 0, bytesRead);
            }
        }
    }
    
    /**
     * 检查 API 服务健康状态
     */
    public static boolean checkHealth() {
        try {
            JSONObject response = httpGet("/health");
            System.out.println("✅ 服务状态: " + response.getString("status"));
            System.out.println("✅ GPU 加速: " + (response.getBoolean("gpu_enabled") ? "已启用" : "未启用"));
            return true;
        } catch (IOException e) {
            System.err.println("❌ 无法连接到服务器: " + API_BASE_URL);
            System.err.println("   错误: " + e.getMessage());
            System.err.println("   请确保 API 服务正在运行");
            return false;
        }
    }
    
    /**
     * 调用 API 生成语音
     */
    public static JSONObject synthesizeSpeech(String text, String voiceStyle, 
                                              int totalSteps, double speed, 
                                              boolean saveFile) {
        try {
            JSONObject payload = new JSONObject();
            payload.put("text", text);
            payload.put("voice_style", voiceStyle);
            payload.put("total_steps", totalSteps);
            payload.put("speed", speed);
            
            System.out.println("📤 发送请求: " + (text.length() > 50 ? text.substring(0, 50) + "..." : text));
            JSONObject result = httpPost("/synthesize", payload);
            
            System.out.println("✅ 生成成功!");
            System.out.println("   文件: " + result.getString("output_file"));
            System.out.println("   生成时间: " + result.getDouble("generation_time") + "秒");
            System.out.println("   音频时长: " + result.getDouble("audio_duration") + "秒");
            System.out.println("   文本长度: " + result.getInt("text_length") + "字符");
            
            // 下载音频文件
            if (saveFile) {
                String filename = result.getString("output_file");
                String savePath = System.getProperty("user.dir") + "/" + filename;
                downloadFile(filename, savePath);
                System.out.println("💾 音频已保存: " + savePath);
            }
            
            return result;
        } catch (IOException e) {
            System.err.println("❌ API 错误: " + e.getMessage());
            return null;
        }
    }
    
    /**
     * 主函数
     */
    public static void main(String[] args) {
        System.out.println("=".repeat(60));
        System.out.println("Supertonic TTS - Java API Client");
        System.out.println("=".repeat(60));
        System.out.println();
        
        // 如果提供了命令行参数，使用第一个参数作为文本
        if (args.length > 0) {
            String text = String.join(" ", args);
            if (checkHealth()) {
                synthesizeSpeech(text, "assets/voice_styles/M1.json", 5, 1.05, true);
            }
            return;
        }
        
        // 1. 检查服务健康状态
        System.out.println("1️⃣ 检查服务状态...");
        if (!checkHealth()) {
            System.exit(1);
        }
        System.out.println();
        
        // 2. 生成语音示例
        System.out.println("2️⃣ 生成语音...");
        
        // 示例 1: 基本使用
        String text1 = "你好，这是 Supertonic TTS 的测试。";
        JSONObject result1 = synthesizeSpeech(
            text1,
            "assets/voice_styles/M1.json",
            5,
            1.05,
            true
        );
        System.out.println();
        
        // 示例 2: 使用不同语音风格
        if (result1 != null) {
            String text2 = "Hello, this is a test of the Supertonic TTS system.";
            JSONObject result2 = synthesizeSpeech(
                text2,
                "assets/voice_styles/F1.json",
                5,
                1.0,
                true
            );
            System.out.println();
        }
        
        // 示例 3: 高质量模式
        if (result1 != null) {
            String text3 = "这是一个高质量语音合成的测试，使用了更多的去噪步骤。";
            JSONObject result3 = synthesizeSpeech(
                text3,
                "assets/voice_styles/M2.json",
                10,  // 更多步数 = 更高质量
                1.05,
                true
            );
            System.out.println();
        }
        
        System.out.println("=".repeat(60));
        System.out.println("✅ 完成!");
        System.out.println("=".repeat(60));
    }
}
