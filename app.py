# AI简报小助手 - 哥特式暗黑版 v2.1
# 原名：VIGIL AETERNUS · 永恒守望者
# 修复：API 密钥状态管理问题

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
// 强制暗黑模式，无视系统设置
document.documentElement.style.colorScheme = 'dark';
if (document.body) {
    document.body.style.backgroundColor = '#050508';
    document.body.style.color = '#a0a0a0';
}

// 录音计时器与状态管理
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
                box-shadow: 0 0 50px rgba(139, 0, 0, 0.5), inset 0 0 30px rgba(139, 0, 0, 0.1);
                backdrop-filter: blur(10px);
            }
            .gothic-eye {
                width: 80px;
                height: 80px;
                margin: 0 auto 20px;
                position: relative;
            }
            .eye-outer {
                width: 100%;
                height: 100%;
                border: 3px solid #8b0000;
                border-radius: 50%;
                position: absolute;
                animation: pulse 2s infinite;
                box-shadow: 0 0 20px rgba(139, 0, 0, 0.6);
            }
            .eye-inner {
                width: 60%;
                height: 60%;
                background: #4a0404;
                border-radius: 50%;
                position: absolute;
                top: 20%;
                left: 20%;
                animation: pulse 1.5s infinite reverse;
            }
            .eye-pupil {
                width: 30%;
                height: 30%;
                background: #ff1a1a;
                border-radius: 50%;
                position: absolute;
                top: 35%;
                left: 35%;
                box-shadow: 0 0 10px #ff1a1a;
            }
            .timer-text {
                font-size: 48px;
                color: #ff1a1a;
                font-family: 'Courier New', monospace;
                font-weight: bold;
                text-shadow: 0 0 10px rgba(255, 26, 26, 0.5);
                margin: 10px 0;
            }
            .timer-label {
                font-size: 14px;
                color: #666;
                font-family: serif;
                letter-spacing: 2px;
            }
            @keyframes pulse {
                0%, 100% { transform: scale(1); opacity: 0.8; }
                50% { transform: scale(1.1); opacity: 1; }
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
    
    const endTime = Date.now();
    const duration = endTime - recordingStartTime;
    const seconds = Math.floor(duration / 1000);
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    const timeStr = (minutes < 10 ? '0' + minutes : minutes) + ':' + (secs < 10 ? '0' + secs : secs);
    
    const overlay = document.getElementById('gothic-timer');
    if (overlay) {
        overlay.innerHTML = `
            <div style="font-size: 60px; color: #8b0000; margin-bottom: 10px;">✦</div>
            <div class="timer-text" style="font-size: 36px; color: #c0c0c0;">${timeStr}</div>
            <div class="timer-label" style="color: #8b0000; margin-top: 10px;">灵魂已捕获</div>
            <div style="font-size: 12px; color: #444; margin-top: 15px;">正在炼金转录...</div>
        `;
        
        setTimeout(function() {
            overlay.style.display = 'none';
        }, 3000);
    }
    
    sessionStorage.setItem('last_recording_duration', timeStr);
    sessionStorage.setItem('last_recording_seconds', seconds.toString());
}

const observer = new MutationObserver(function(mutations) {
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        const text = button.textContent || button.innerText;
        if ((text.includes('开始') || text.includes('🩸')) && !isRecording && !button.hasAttribute('data-listening')) {
            button.setAttribute('data-listening', 'true');
            button.addEventListener('click', startRecordingTimer);
        }
        if ((text.includes('停止') || text.includes('⏹')) && isRecording && !button.hasAttribute('data-stopping')) {
            button.setAttribute('data-stopping', 'true');
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
:root {
    --bg-primary: #050508;
    --bg-secondary: #0a0a0f;
    --bg-tertiary: #1a1a20;
    --accent-blood: #8b0000;
    --accent-bright: #ff1a1a;
    --accent-gold: #3a3a2a;
    --text-primary: #c0c0c0;
    --text-secondary: #666666;
    --text-muted: #444444;
    --border-color: #2a2a30;
    --glow-red: rgba(139, 0, 0, 0.3);
}

.stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Courier New', 'Cinzel', serif !important;
}

header[data-testid="stHeader"] {
    display: none;
}

.main .block-container {
    background-color: var(--bg-primary);
    padding: 2rem;
    max-width: 1200px;
}

.gothic-title {
    font-size: 42px;
    color: var(--text-primary);
    text-align: center;
    font-weight: bold;
    letter-spacing: 8px;
    text-transform: uppercase;
    margin-bottom: 5px;
    text-shadow: 0 0 20px rgba(139, 0, 0, 0.5);
    font-family: 'Cinzel', 'Trajan Pro', serif !important;
    border-bottom: 2px solid var(--accent-blood);
    padding-bottom: 15px;
    position: relative;
}

.gothic-title::before,
.gothic-title::after {
    content: '◈';
    color: var(--accent-blood);
    margin: 0 20px;
    font-size: 24px;
}

.gothic-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    text-align: center;
    font-style: italic;
    letter-spacing: 4px;
    margin-bottom: 40px;
    font-family: serif;
}

.gothic-panel {
    background-color: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 25px;
    margin: 10px 0;
    position: relative;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.05);
}

.gothic-panel::before {
    content: '';
    position: absolute;
    top: -1px;
    left: 20%;
    right: 20%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-blood), transparent);
}

.panel-title {
    font-size: 16px;
    color: var(--text-primary);
    font-weight: bold;
    letter-spacing: 3px;
    margin-bottom: 20px;
    text-align: center;
    text-transform: uppercase;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.panel-title::before,
.panel-title::after {
    content: '◆';
    color: var(--accent-blood);
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
    border: 3px solid var(--accent-blood);
    border-radius: 50%;
    position: absolute;
    transition: all 0.3s ease;
    box-shadow: 0 0 30px rgba(139, 0, 0, 0.4);
}

.eye-inner {
    width: 60%;
    height: 60%;
    background: linear-gradient(135deg, var(--accent-blood), #2a0000);
    border-radius: 50%;
    position: absolute;
    top: 20%;
    left: 20%;
    transition: all 0.3s ease;
}

.eye-pupil {
    width: 30%;
    height: 30%;
    background: var(--accent-bright);
    border-radius: 50%;
    position: absolute;
    top: 35%;
    left: 35%;
    box-shadow: 0 0 15px var(--accent-bright);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 25px var(--accent-bright); }
}

.stButton>button {
    background: linear-gradient(135deg, #1a0000, #2a0000) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--accent-blood) !important;
    border-radius: 4px !important;
    padding: 12px 24px !important;
    font-family: 'Courier New', monospace !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    font-size: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    position: relative;
    overflow: hidden;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #2a0000, #3a0000) !important;
    border-color: var(--accent-bright) !important;
    box-shadow: 0 0 20px rgba(139, 0, 0, 0.4) !important;
    transform: translateY(-2px);
}

.stButton>button:active {
    transform: translateY(0);
}

.stButton>button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-blood), #4a0000) !important;
    border-color: var(--accent-bright) !important;
    color: white !important;
    font-weight: bold !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background-color: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 4px !important;
    font-family: 'Courier New', monospace !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.5) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent-blood) !important;
    box-shadow: 0 0 10px rgba(139, 0, 0, 0.2), inset 0 2px 4px rgba(0,0,0,0.5) !important;
}

.stTextArea textarea {
    min-height: 300px !important;
    line-height: 1.8 !important;
}

.css-1d391kg, .css-163ttbj, section[data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border-color) !important;
}

section[data-testid="stSidebar"] .block-container {
    background-color: transparent !important;
}

.stFileUploader > div > div {
    background-color: var(--bg-tertiary) !important;
    border: 2px dashed var(--border-color) !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
}

.stFileUploader > div > div:hover {
    border-color: var(--accent-blood) !important;
    background-color: rgba(139, 0, 0, 0.05) !important;
}

.stAlert {
    background-color: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-color) !important;
    border-left: 4px solid var(--accent-blood) !important;
    border-radius: 4px !important;
}

.stSuccess {
    border-left-color: #1a4a1a !important;
    background-color: rgba(26, 74, 26, 0.1) !important;
}

.stError {
    border-left-color: var(--accent-bright) !important;
    background-color: rgba(255, 26, 26, 0.05) !important;
}

hr {
    border-color: var(--border-color) !important;
    margin: 30px 0 !important;
    position: relative;
}

hr::after {
    content: '◈';
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    background: var(--bg-primary);
    color: var(--accent-blood);
    padding: 0 10px;
    font-size: 12px;
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: var(--text-secondary);
    letter-spacing: 1px;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--accent-blood);
    animation: blink 2s infinite;
    box-shadow: 0 0 10px var(--accent-blood);
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.timer-display {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, rgba(139,0,0,0.1), transparent);
    border: 1px solid var(--accent-blood);
    border-radius: 8px;
    margin: 20px 0;
}

.timer-value {
    font-size: 36px;
    color: var(--accent-bright);
    font-family: 'Courier New', monospace;
    font-weight: bold;
    text-shadow: 0 0 10px rgba(255, 26, 26, 0.3);
    letter-spacing: 4px;
}

.output-scroll {
    background-color: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 20px;
    max-height: 400px;
    overflow-y: auto;
    font-family: 'Courier New', monospace;
    line-height: 1.8;
    color: var(--text-primary);
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
    background: var(--accent-blood);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--accent-bright);
}

.stDownloadButton > button {
    background: var(--bg-tertiary) !important;
    border-color: var(--border-color) !important;
    color: var(--text-secondary) !important;
}

.stDownloadButton > button:hover {
    border-color: var(--accent-blood) !important;
    color: var(--text-primary) !important;
}

@media (max-width: 768px) {
    .gothic-title { font-size: 28px; letter-spacing: 4px; }
    .gothic-title::before, .gothic-title::after { display: none; }
    .main .block-container { padding: 1rem; }
}

.stSpinner > div {
    border-top-color: var(--accent-blood) !important;
    border-right-color: transparent !important;
    border-bottom-color: var(--accent-blood) !important;
    border-left-color: transparent !important;
}

p, h1, h2, h3, h4, h5, h6, span, label, .stMarkdown {
    color: var(--text-primary) !important;
}

div[role="listbox"] div {
    background-color: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

div[role="option"]:hover {
    background-color: rgba(139, 0, 0, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ========== 核心功能函数 ==========
def transcribe_audio(audio_bytes, api_key):
    """语音转文字 - 炼金术核心"""
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
        return {"success": True, "text": transcription}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_briefing(content, briefing_type, custom_req, api_key):
    """生成简报 - 炼金术转化"""
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

# ========== API 密钥管理（修复版）==========
# 优先从 secrets 获取，否则从 session_state 获取
api_key = None

# 首先检查 st.secrets（部署环境）
try:
    api_key = st.secrets.get("SILICONFLOW_API_KEY", "")
except:
    pass

# 如果 secrets 中没有，检查 session_state（用户输入）
if not api_key:
    api_key = st.session_state.get("api_key", "")

# 如果都没有，显示输入界面
if not api_key:
    st.markdown('<div class="gothic-title">VIGIL AETERNUS</div>', unsafe_allow_html=True)
    st.markdown('<div class="gothic-subtitle">永恒守望者 · 语音炼金术</div>', unsafe_allow_html=True)
    
    with st.expander("🔑 唤醒炼金引擎（输入API密钥）", expanded=True):
        st.markdown("""
        <div style="background: rgba(139,0,0,0.05); padding: 20px; border-radius: 8px; border-left: 3px solid #8b0000;">
            <p style="margin: 0; color: #888; font-family: serif;">
                要启动这台古老的语音炼金装置，你需要提供灵魂密钥：<br><br>
                1. 前往 <a href="https://siliconflow.cn" style="color: #ff1a1a;">siliconflow.cn</a> 进行血之契约（注册）<br>
                2. 在祭坛上创建 API 密钥<br>
                3. 将密钥刻入下方石碑
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
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⚡ 激活炼金引擎", type="primary", use_container_width=True):
                if api_input and api_input.startswith("sk-"):
                    # 保存到 session_state
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

# 侧边栏 - 暗影之书
with st.sidebar:
    st.markdown('<div style="text-align: center; color: #8b0000; font-size: 24px; margin-bottom: 20px;">◈</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #c0c0c0; font-family: serif; letter-spacing: 3px; margin-bottom: 30px;">炼金日志</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="status-indicator" style="margin-bottom: 20px;">
        <div class="status-dot"></div>
        <span>引擎运转中</span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗝️ 更换密钥", use_container_width=True):
        if "api_key" in st.session_state:
            del st.session_state.api_key
        st.rerun()
    
    st.divider()
    
    st.markdown('<div style="color: #666; font-size: 11px; letter-spacing: 2px; margin-bottom: 10px;">已捕获灵魂残片</div>', unsafe_allow_html=True)
    count = st.session_state.get("transcription_count", 0)
    st.markdown(f'<div style="color: #8b0000; font-size: 28px; font-family: monospace; text-align: center;">{count:,}</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("v2.1 · 哥特式暗黑版 · 已修复")

# 主界面 - 三栏炼金工坊
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# ========== 左栏：灵魂捕获 ==========
with col_left:
    st.markdown("""
    <div class="gothic-panel">
        <div class="panel-title">灵魂捕获</div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="eye-button" onclick="document.querySelector('button[kind=secondary]').click()">
        <div class="eye-outer"></div>
        <div class="eye-inner"></div>
        <div class="eye-pupil"></div>
    </div>
    <div style="text-align: center; color: #666; font-size: 11px; letter-spacing: 2px; margin-top: -10px; margin-bottom: 20px;">
        点击启动聆听仪式
    </div>
    """, unsafe_allow_html=True)
    
    try:
        from streamlit_mic_recorder import mic_recorder
        
        audio = mic_recorder(
            start_prompt="🩸 开始聆听",
            stop_prompt="⏹ 封印灵魂",
            just_once=True,
            key="gothic_recorder"
        )
        
        if audio and audio.get("bytes"):
            bytes_data = audio["bytes"]
            sample_rate = audio.get("sample_rate", 16000)
            sample_width = audio.get("sample_width", 2)
            duration_seconds = len(bytes_data) / (sample_rate * sample_width)
            minutes = int(duration_seconds // 60)
            seconds = int(duration_seconds % 60)
            duration_str = f"{minutes:02d}:{seconds:02d}"
            
            st.markdown(f"""
            <div class="timer-display">
                <div class="timer-value">{duration_str}</div>
                <div style="color: #666; font-size: 11px; letter-spacing: 2px;">灵魂时长</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner("⚗️ 炼金转录中..."):
                result = transcribe_audio(audio["bytes"], api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.session_state.last_duration = duration_str
                    st.session_state.transcription_count = st.session_state.get("transcription_count", 0) + 1
                    st.success(f"✦ 灵魂已捕获 | {len(result['text'])} 字符")
                    st.rerun()
                else:
                    st.error(f"✦ 转录失败: {result['error']}")
                    
    except ImportError:
        st.error("⚠️ 录音组件未就绪")
    
    st.divider()
    
    st.markdown('<div style="color: #888; font-size: 12px; margin-bottom: 10px;">或上传记忆残片</div>', unsafe_allow_html=True)
    
    audio_file = st.file_uploader(
        "选择录音",
        type=['mp3', 'wav', 'm4a', 'webm'],
        label_visibility="collapsed"
    )
    
    if audio_file:
        st.audio(audio_file, format=f'audio/{audio_file.type.split("/")[1]}')
        
        if st.button("⚗️ 炼金转录", key="upload_transcribe", use_container_width=True):
            with st.spinner("⚗️ 正在解析灵魂印记..."):
                result = transcribe_audio(audio_file.getvalue(), api_key)
                
                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.session_state.transcription_count = st.session_state.get("transcription_count", 0) + 1
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
    
    briefing_type = st.selectbox(
        "炼金仪式类型",
        ["会议纪要", "工作日报", "学习笔记", "新闻摘要"],
        key="briefing_type"
    )
    
    default_text = st.session_state.get("transcribed_text", "")
    
    content = st.text_area(
        "原始灵魂印记",
        value=default_text,
        height=280,
        placeholder="在此刻下你的话语，或等待语音捕获...\n\n如同在羊皮纸上书写，每一个字都将被永恒铭记。",
        key="content_editor"
    )
    
    if content != st.session_state.get("transcribed_text", ""):
        st.session_state.transcribed_text = content
    
    custom_req = st.text_input(
        "特殊炼金指令",
        placeholder="例如：强调时间紧迫性、突出风险...",
        key="custom_requirements"
    )
    
    col_gen, col_clear = st.columns([2, 1])
    
    with col_gen:
        if st.button("⚡ 启动炼金术", type="primary", use_container_width=True):
            if not content.strip():
                st.error("✦ 没有可炼金的素材 ✦")
            else:
                with st.spinner("⚗️ 炼金转化中..."):
                    result = generate_briefing(content, briefing_type, custom_req, api_key)
                    
                    if result["success"]:
                        st.session_state.generated_result = result["text"]
                        st.balloons()
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
                ◈ {briefing_type} ◈
            </div>
            <div style="white-space: pre-wrap;">{result_text}</div>
            <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #2a2a30; color: #444; font-size: 10px; text-align: right;">
                生成于 {time.strftime("%H:%M")}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_dl, col_copy = st.columns(2)
        
        with col_dl:
            st.download_button(
                "⬇ 封存卷轴",
                result_text,
                file_name=f"{briefing_type}_{time.strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True
            )
        
        with col_copy:
            if st.button("📋 复制", use_container_width=True):
                st.toast("✦ 已复制到剪贴板 ✦")
    else:
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px; color: #333; font-style: italic;">
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
<div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #1a1a20; color: #333; font-size: 11px; letter-spacing: 3px; font-family: serif;">
    ✦ MEMENTO MORI ✦<br>
    <span style="font-size: 9px; opacity: 0.6;">记住你终将死去，因此每一句话都值得被铭记</span>
</div>
""", unsafe_allow_html=True)

st.caption("")
