# AI简报小助手 - 哥特式暗黑版 v2.7
# 修复：API 密钥持久化存储（使用浏览器 localStorage）

import streamlit as st
from openai import OpenAI
import os
import tempfile
import time

# ========== 强制暗黑模式配置 ==========
st.markdown("""
<!-- 强制暗黑主题 -->
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0a0a0f">

<!-- PWA配置 -->
<link rel="manifest" href="manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="VIGIL AETERNUS">

<!-- 哥特式图标 -->
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🩸</text></svg>">

<script>
// 强制暗黑模式
document.documentElement.style.colorScheme = 'dark';
if (document.body) {
    document.body.style.backgroundColor = '#050508';
    document.body.style.color = '#a0a0a0';
}

// API 密钥持久化存储
function saveApiKey(key) {
    localStorage.setItem('vigil_aeternus_api_key', key);
    console.log('API 密钥已保存到本地存储');
}

function getApiKey() {
    return localStorage.getItem('vigil_aeternus_api_key');
}

function clearApiKey() {
    localStorage.removeItem('vigil_aeternus_api_key');
}

// 页面加载时检查是否有存储的密钥
window.addEventListener('load', function() {
    const storedKey = getApiKey();
    if (storedKey) {
        console.log('发现存储的 API 密钥');
        // 将密钥发送到 Streamlit
        const input = document.querySelector('input[type="password"]');
        if (input && !input.value) {
            input.value = storedKey;
            input.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
});

// 录音计时器
let recordingTimer = null;
let recordingStartTime = null;
let isRecording = false;

function startRecordingTimer() {
    if (isRecording) return;
    isRecording = true;
    recordingStartTime = Date.now();
    
    let overlay = document.getElementById('gothic-timer');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'gothic-timer';
        overlay.innerHTML = `
            <div class="gothic-eye">
                <div class="eye-outer"></div>
                <div class="eye-inner"></div>
                <div class="eye-pupil"></div>
            </div>
            <div class="timer-text">00:00</div>
            <div class="timer-label">◉ 聆听灵魂低语中</div>
        `;
        document.body.appendChild(overlay);
        
        const style = document.createElement('style');
        style.textContent = `
            #gothic-timer {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 999999;
                text-align: center;
                background: rgba(10, 10, 15, 0.95);
                border: 2px solid #8b0000;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 0 50px rgba(139, 0, 0, 0.5);
            }
            .gothic-eye { width: 80px; height: 80px; margin: 0 auto 20px; position: relative; }
            .eye-outer {
                width: 100%; height: 100%;
                border: 3px solid #8b0000;
                border-radius: 50%;
                position: absolute;
                animation: pulse 2s infinite;
            }
            .eye-inner {
                width: 60%; height: 60%;
                background: #4a0404;
                border-radius: 50%;
                position: absolute;
                top: 20%; left: 20%;
            }
            .eye-pupil {
                width: 30%; height: 30%;
                background: #ff1a1a;
                border-radius: 50%;
                position: absolute;
                top: 35%; left: 35%;
                box-shadow: 0 0 10px #ff1a1a;
            }
            .timer-text {
                font-size: 48px;
                color: #ff1a1a;
                font-family: monospace;
                font-weight: bold;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
        `;
        document.head.appendChild(style);
    }
    overlay.style.display = 'block';
    
    recordingTimer = setInterval(function() {
        const elapsed = Date.now() - recordingStartTime;
        const seconds = Math.floor(elapsed / 1000);
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        const timeStr = (minutes < 10 ? '0' + minutes : minutes) + ':' + (secs < 10 ? '0' + secs : secs);
        const timerText = overlay.querySelector('.timer-text');
        if (timerText) timerText.textContent = timeStr;
    }, 1000);
}

function stopRecordingTimer() {
    if (!isRecording) return;
    isRecording = false;
    clearInterval(recordingTimer);
    
    const overlay = document.getElementById('gothic-timer');
    if (overlay) {
        overlay.innerHTML = `
            <div style="font-size: 60px; color: #8b0000;">✦</div>
            <div style="font-size: 36px; color: #c0c0c0; margin: 10px 0;">灵魂已捕获</div>
            <div style="font-size: 12px; color: #666;">正在炼金转录...</div>
        `;
        setTimeout(() => overlay.style.display = 'none', 2000);
    }
}

// 监听按钮
const observer = new MutationObserver(function(mutations) {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        const text = button.textContent || '';
        if ((text.includes('开始') || text.includes('🩸')) && !isRecording) {
            button.addEventListener('click', startRecordingTimer);
        }
        if ((text.includes('停止') || text.includes('⏹')) && isRecording) {
            button.addEventListener('click', stopRecordingTimer);
        }
    });
});
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# ========== 页面设置 ==========
st.set_page_config(
    page_title="VIGIL AETERNUS · 永恒守望者", 
    page_icon="🩸",
    initial_sidebar_state="expanded",
    layout="wide"
)

# ========== 哥特式暗黑CSS ==========
st.markdown("""
<style>
/* 强制暗黑基础变量 */
:root {
    --bg-primary: #050508 !important;
    --bg-secondary: #0a0a0f !important;
    --bg-tertiary: #1a1a20 !important;
    --accent-blood: #8b0000 !important;
    --accent-bright: #ff1a1a !important;
    --accent-gold: #3a3a2a !important;
    --text-primary: #c0c0c0 !important;
    --text-secondary: #666666 !important;
    --text-muted: #444444 !important;
    --border-color: #2a2a30 !important;
}

@media (prefers-color-scheme: light) {
    .stApp { background-color: #050508 !important; }
}

.stApp {
    background-color: #050508 !important;
    color: #c0c0c0 !important;
    font-family: 'Courier New', serif !important;
}

header[data-testid="stHeader"] { display: none; }

.main .block-container {
    background-color: #050508 !important;
    padding: 2rem;
    max-width: 1200px;
}

.gothic-title {
    font-size: 42px;
    color: #c0c0c0 !important;
    text-align: center !important;
    font-weight: bold;
    letter-spacing: 8px;
    text-transform: uppercase;
    margin-bottom: 5px;
    text-shadow: 0 0 20px rgba(139, 0, 0, 0.5);
    border-bottom: 2px solid #8b0000;
    padding-bottom: 15px;
    word-wrap: break-word;
    white-space: normal;
    line-height: 1.2;
    display: block;
    width: 100%;
}

@media (max-width: 768px) {
    .gothic-title {
        font-size: 28px !important;
        letter-spacing: 4px !important;
        padding: 0 10px;
    }
    .gothic-title::before, .gothic-title::after { display: none !important; }
}

.gothic-title::before, .gothic-title::after {
    content: '◈';
    color: #8b0000;
    margin: 0 20px;
    font-size: 24px;
}

.gothic-subtitle {
    font-size: 14px;
    color: #666666 !important;
    text-align: center;
    font-style: italic;
    letter-spacing: 4px;
    margin-bottom: 40px;
}

.gothic-panel {
    background-color: #0a0a0f !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 8px;
    padding: 25px;
    margin: 10px 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.panel-title {
    font-size: 16px;
    color: #c0c0c0 !important;
    font-weight: bold;
    letter-spacing: 3px;
    margin-bottom: 20px;
    text-align: center;
    text-transform: uppercase;
    border-bottom: 1px solid #2a2a30;
    padding-bottom: 10px;
}

.panel-title::before, .panel-title::after {
    content: '◆';
    color: #8b0000;
    margin: 0 10px;
    font-size: 12px;
}

.eye-button {
    width: 120px;
    height: 120px;
    margin: 20px auto;
    position: relative;
    cursor: pointer;
}

.eye-outer {
    width: 100%;
    height: 100%;
    border: 3px solid #8b0000;
    border-radius: 50%;
    position: absolute;
    box-shadow: 0 0 30px rgba(139, 0, 0, 0.4);
}

.eye-inner {
    width: 60%;
    height: 60%;
    background: linear-gradient(135deg, #8b0000, #2a0000);
    border-radius: 50%;
    position: absolute;
    top: 20%;
    left: 20%;
}

.eye-pupil {
    width: 30%;
    height: 30%;
    background: #ff1a1a;
    border-radius: 50%;
    position: absolute;
    top: 35%;
    left: 35%;
    box-shadow: 0 0 15px #ff1a1a;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 1; }
}

.stButton>button {
    background: linear-gradient(135deg, #1a0000, #2a0000) !important;
    color: #c0c0c0 !important;
    border: 1px solid #8b0000 !important;
    border-radius: 4px !important;
    padding: 12px 24px !important;
    font-family: 'Courier New', monospace !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    transition: all 0.3s ease !important;
    -webkit-appearance: none !important;
    appearance: none !important;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #2a0000, #3a0000) !important;
    border-color: #ff1a1a !important;
    box-shadow: 0 0 20px rgba(139, 0, 0, 0.4) !important;
}

.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, #8b0000, #4a0000) !important;
    border-color: #ff1a1a !important;
    color: white !important;
    font-weight: bold !important;
}

.stFileUploader > div > div {
    background-color: #1a1a20 !important;
    border: 1px dashed #8b0000 !important;
    color: #c0c0c0 !important;
    border-radius: 8px !important;
}

.stFileUploader section > div > div > span { display: none !important; }
.stFileUploader section > div > div::before {
    content: "将记忆残片拖拽至此" !important;
    color: #c0c0c0 !important;
    font-size: 16px !important;
}
.stFileUploader section > div > div > small { display: none !important; }
.stFileUploader section > div > div::after {
    content: "每个残片限 200MB 以内" !important;
    color: #666 !important;
    font-size: 12px !important;
    display: block !important;
    margin-top: 5px !important;
}
.stFileUploader button { font-size: 0 !important; }
.stFileUploader button::before {
    content: "时光回流" !important;
    font-size: 12px !important;
}

.stFileUploader > div > div:hover {
    border-color: #8b0000 !important;
    background-color: rgba(139, 0, 0, 0.05) !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background-color: #1a1a20 !important;
    color: #c0c0c0 !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 4px !important;
    font-family: 'Courier New', monospace !important;
}

.stTextArea textarea {
    min-height: 300px !important;
    line-height: 1.8 !important;
}

section[data-testid="stSidebar"] {
    background-color: #0a0a0f !important;
    border-right: 1px solid #2a2a30 !important;
}

.stAlert {
    background-color: #1a1a20 !important;
    color: #c0c0c0 !important;
    border-left: 4px solid #8b0000 !important;
}

.timer-display {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, rgba(139,0,0,0.1), transparent);
    border: 1px solid #8b0000;
    border-radius: 8px;
    margin: 20px 0;
}

.timer-value {
    font-size: 36px;
    color: #ff1a1a;
    font-family: 'Courier New', monospace;
    font-weight: bold;
    letter-spacing: 4px;
}

.output-scroll {
    background-color: #1a1a20 !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 4px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    line-height: 1.8;
    color: #c0c0c0 !important;
}

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb {
    background: #8b0000;
    border-radius: 4px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #8b0000;
    animation: blink 2s infinite;
    display: inline-block;
    margin-right: 8px;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

p, h1, h2, h3, h4, h5, h6, span, label, .stMarkdown {
    color: #c0c0c0 !important;
}

div[role="listbox"] div {
    background-color: #1a1a20 !important;
    color: #c0c0c0 !important;
}

div[role="option"]:hover {
    background-color: rgba(139, 0, 0, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ========== 核心功能函数 ==========
def transcribe_audio(audio_bytes, api_key):
    """语音转文字"""
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        with open(tmp_path, "rb") as audio:
            transcription = client.audio.transcriptions.create(
                model="FunAudioLLM/SenseVoiceSmall",
                file=audio,
                response_format="text"
            )
        
        os.unlink(tmp_path)
        clean_text = str(transcription)
        if clean_text.startswith('{') and '"text"' in clean_text:
            try:
                import json
                data = json.loads(clean_text)
                clean_text = data.get("text", clean_text)
            except:
                pass
        
        return {"success": True, "text": clean_text}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_briefing(content, briefing_type, custom_req, api_key):
    """生成简报"""
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.siliconflow.cn/v1")
        
        prompts = {
            "会议纪要": """你是一位精通暗影艺术的书记官。请将以下语音内容整理成庄严的会议纪要：
            
一、仪式主题（会议主题）
二、参与者低语（与会人员发言要点）
三、血之契约（决议事项）
四、未竟之事（待办事项）

使用肃穆、简洁的语言，如同刻在石碑上的铭文。""",
            
            "工作日报": """作为时间的记录者，将以下内容转化为每日仪式报告：
            
├─ 已完成之业
├─ 受阻之困  
├─ 明日之誓

语言应如暗夜中的钟声，清晰而沉重。""",
            
            "学习笔记": """以古老智者的口吻，将知识整理成永恒的智慧卷轴：
            
◈ 核心真理（概念定义）
◈ 深渊启示（重点难点）
◈ 灵魂反思（个人思考）

文字应带有神秘学的庄重感。""",
            
            "新闻摘要": """作为历史的见证者，将事件记录成不朽的档案：
            
【事件本质】
【关键数据】
【深远影响】

语气应客观如死神，精准如刀刃。"""
        }
        
        prompt = prompts.get(briefing_type, prompts["会议纪要"])
        if custom_req:
            prompt += f"\n\n特殊炼金要求：{custom_req}"
        
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {"success": True, "text": response.choices[0].message.content}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== 初始化 Session State ==========
if "transcribed_text" not in st.session_state:
    st.session_state.transcribed_text = ""
if "generated_result" not in st.session_state:
    st.session_state.generated_result = ""

# ========== API 密钥管理（优化：自动获取 + 持久化存储）==========

# 1. 优先从 session_state 获取（当前会话或刚输入的情况）
api_key = st.session_state.get("api_key", "")

# 2. 其次尝试从 st.secrets 自动获取（Streamlit Cloud 部署环境）
if not api_key:
    try:
        # 兼容两种可能的密钥名称
        api_key = st.secrets.get("SILICONFLOW_API_KEY") or st.secrets.get("api_key")
        if api_key:
            st.session_state.api_key = api_key
    except:
        pass

# 3. 如果都没有，显示输入界面
if not api_key:
    st.markdown('<div class="gothic-title">VIGIL AETERNUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="gothic-subtitle">永恒守望者 · 语音炼金术</div>', unsafe_allow_html=True)
    
    with st.expander("🔑 唤醒炼金引擎（输入API密钥）", expanded=True):
        st.markdown("""
        <div style="background: rgba(139,0,0,0.05); padding: 20px; border-radius: 8px; border-left: 3px solid #8b0000;">
            <p style="margin: 0; color: #888;">
                要启动这台古老的语音炼金装置，你需要提供灵魂密钥：<br><br>
                1. 前往 <a href="https://siliconflow.cn" style="color: #ff1a1a;">siliconflow.cn</a> 进行血之契约（注册）<br>
                2. 在祭坛上创建 API 密钥<br>
                3. 将密钥刻入下方石碑<br><br>
                <small style="color: #666;">密钥将被保存在浏览器本地存储中，下次无需重复输入</small>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        api_input = st.text_input(
            "API 密钥",
            value="",
            type="password",
            placeholder="sk-xxxxxxxxxxxxxxxx",
            key="api_key_input"
        )
        
        # 添加 JavaScript 保存功能
        if api_input:
            st.markdown(f"""
            <script>
                saveApiKey('{api_input}');
            </script>
            """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡ 激活炼金引擎", type="primary", use_container_width=True):
                if api_input and api_input.startswith("sk-"):
                    st.session_state.api_key = api_input
                    st.success("✦ 炼金引擎已唤醒 ✦")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("✦ 无效的密钥格式 ✦")
    
    st.stop()

# ========== 主应用界面 ==========
st.markdown('<div class="gothic-title">VIGIL AETERNUS</div>', unsafe_allow_html=True)
st.markdown('<div class="gothic-subtitle">永恒守望者 · 语音炼金术</div>', unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.markdown('<div style="text-align: center; color: #8b0000; font-size: 24px; margin-bottom: 20px;">◈</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #c0c0c0; letter-spacing: 3px; margin-bottom: 30px;">炼金日志</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="margin-bottom: 20px; color: #666; font-size: 11px;">
        <span class="status-dot"></span>
        <span>引擎运转中</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗝️ 更换密钥", use_container_width=True):
        # 清除 session_state 和浏览器存储
        if "api_key" in st.session_state:
            del st.session_state.api_key
        st.markdown("""
        <script>clearApiKey();</script>
        """, unsafe_allow_html=True)
        st.rerun()
    
    st.divider()
    st.caption("v2.7 · 密钥持久化存储")

# 主界面 - 三栏布局
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# ========== 左栏：灵魂捕获 ==========
with col_left:
    st.markdown("""
    <div class="gothic-panel">
        <div class="panel-title">灵魂捕获</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="eye-button">
        <div class="eye-outer"></div>
        <div class="eye-inner"></div>
        <div class="eye-pupil"></div>
    </div>
    <div style="text-align: center; color: #666; font-size: 11px; letter-spacing: 2px; margin-bottom: 20px;">
        点击启动聆听仪式
    </div>
    """, unsafe_allow_html=True)
    
    # 实时录音
    try:
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="🩸 开始聆听",
            stop_prompt="⏹ 封印灵魂",
            just_once=True,
            key="mic_recorder_ios"
        )
        
        if audio and audio.get("bytes"):
            with st.spinner("⚗️ 炼金转录中..."):
                result = transcribe_audio(audio["bytes"], api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success(f"✦ 灵魂已捕获 | {len(result['text'])} 字符")
                    st.rerun()
                else:
                    st.error(f"✦ 转录失败: {result['error']}")
                    
    except ImportError:
        st.error("⚠️ 录音组件未就绪")
    
    st.divider()
    
    # 文件上传
    st.markdown('<div style="color: #888; font-size: 12px; margin-bottom: 10px;">或上传记忆残片</div>', unsafe_allow_html=True)
    
    audio_file = st.file_uploader(
        "选择录音",
        type=['mp3', 'wav', 'm4a', 'webm'],
        label_visibility="collapsed",
        key="audio_upload"
    )
    
    if audio_file:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[1]}')
        
        if st.button("⚗️ 炼金转录", key="upload_transcribe", use_container_width=True):
            with st.spinner("⚗️ 正在解析灵魂印记..."):
                result = transcribe_audio(audio_file.getvalue(), api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success(f"✦ 转录完成 | {len(result['text'])} 字符")
                    st.rerun()
                else:
                    st.error(f"✦ 失败: {result['error']}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== 中栏：炼金工坊 ==========
with col_center:
    st.markdown("""
    <div class="gothic-panel" style="border-color: #8b0000;">
        <div class="panel-title" style="color: #ff1a1a;">炼金工坊</div>
    """, unsafe_allow_html=True)
    
    ritual_mapping = {
        "仪式记录": "会议纪要",
        "昼夜之誓": "工作日报",
        "智慧秘卷": "学习笔记",
        "世界余响": "新闻摘要"
    }
    
    selected_ritual = st.selectbox(
        "炼金仪式类型",
        options=list(ritual_mapping.keys()),
        key="briefing_type_select"
    )
    
    briefing_type = ritual_mapping[selected_ritual]
    
    default_text = st.session_state.get("transcribed_text", "")
    
    content = st.text_area(
        "原始灵魂印记",
        value=default_text,
        height=300,
        placeholder="是原始灵魂的捕获，抑或是记忆碎片的再现..."
    )
    
    if content != st.session_state.get("transcribed_text", ""):
        st.session_state.transcribed_text = content
    
    custom_req = st.text_input("特殊炼金指令", placeholder="听灵魂出窍的声音...")
    
    col_gen, col_clear = st.columns([3, 1])
    
    with col_gen:
        if st.button("⚡ 启动炼金术", type="primary", use_container_width=True):
            if not content.strip():
                st.error("✦ 没有可炼金的素材 ✦")
            else:
                with st.spinner("⚗️ 炼金转化中..."):
                    result = generate_briefing(content, briefing_type, custom_req, api_key)
                    
                    if result["success"]:
                        st.session_state.generated_result = result["text"]
                        st.rerun()
                    else:
                        st.error(f"✦ 炼金失败: {result['error']}")
    
    with col_clear:
        if st.button("🗑️ 净化", use_container_width=True):
            st.session_state.transcribed_text = ""
            if "generated_result" in st.session_state:
                del st.session_state.generated_result
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== 右栏：预言书卷 ==========
with col_right:
    st.markdown("""
    <div class="gothic-panel">
        <div class="panel-title">预言书卷</div>
    """, unsafe_allow_html=True)
    
    if "generated_result" in st.session_state:
        result_text = st.session_state.generated_result
        
        st.markdown(f"""
        <div class="output-scroll">
            <div style="color: #8b0000; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #2a2a30; padding-bottom: 10px;">
                ◈ {selected_ritual} ◈
            </div>
            <div style="white-space: pre-wrap;">{result_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            "⬇ 封存卷轴",
            result_text,
            file_name=f"{selected_ritual}_{time.strftime('%Y%m%d_%H%M')}.txt",
            use_container_width=True
        )
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: #333;">
            <div style="font-size: 48px; margin-bottom: 20px; opacity: 0.3;">◈</div>
            <div style="font-size: 12px; letter-spacing: 2px;">
                等待炼金术启动<br>
                预言将在此显现
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# 底部装饰
st.markdown("""
<div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a1a20; color: #333; font-size: 11px; letter-spacing: 3px;">
    ✦ MEMENTO MORI ✦<br>
    <span style="font-size: 9px; opacity: 0.6;">记住你终将死去，因此每一句话都值得被铭记</span>
</div>
""", unsafe_allow_html=True)

st.caption("")
