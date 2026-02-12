# AI简报小助手 - 哥特式暗黑版 v2.2
# 安全增强版：
# 1. 修复临时文件未删除风险
# 2. 更严格 API Key 校验
# 3. 更安全的异常处理
# 4. 优化 session_state 管理
# 5. 增强错误提示

import streamlit as st
from openai import OpenAI
import os
import tempfile
import time
import re

# ================= 页面配置（必须最前） =================
st.set_page_config(
    page_title="VIGIL AETERNUS · 永恒守望者",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= 安全函数 =================

def validate_api_key(key: str) -> bool:
    """
    更严格的 API Key 校验
    """
    if not key:
        return False
    if not key.startswith("sk-"):
        return False
    if len(key) < 20:
        return False
    if not re.match(r"^sk-[A-Za-z0-9\-_]+$", key):
        return False
    return True


def get_api_key():
    """
    优先读取 secrets
    其次读取 session_state
    """
    try:
        if "SILICONFLOW_API_KEY" in st.secrets:
            return st.secrets["SILICONFLOW_API_KEY"]
    except Exception:
        pass

    return st.session_state.get("api_key", "")


# ================= 核心功能 =================

def transcribe_audio(audio_bytes, api_key):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_bytes)
                tmp_path = tmp_file.name

            with open(tmp_path, "rb") as audio:
                transcription = client.audio.transcriptions.create(
                    model="FunAudioLLM/SenseVoiceSmall",
                    file=audio,
                    response_format="text"
                )

            return {"success": True, "text": transcription}

        finally:
            # 确保一定删除临时文件
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_briefing(content, briefing_type, custom_req, api_key):
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.siliconflow.cn/v1"
        )

        prompts = {
            "会议纪要": "请整理为清晰、专业的会议纪要，包含主题、讨论要点、决议事项和待办事项。",
            "工作日报": "请整理为结构清晰的工作日报，包含已完成、问题、明日计划。",
            "学习笔记": "请整理为结构清晰的学习笔记，包含核心概念、重点、个人思考。",
            "新闻摘要": "请整理为新闻摘要，包含事件概述、关键数据、影响分析。"
        }

        system_prompt = prompts.get(briefing_type, prompts["会议纪要"])

        if custom_req:
            system_prompt += f"\n额外要求：{custom_req}"

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        return {
            "success": True,
            "text": response.choices[0].message.content
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# ================= API KEY 管理 =================

api_key = get_api_key()

if not validate_api_key(api_key):

    st.title("🔐 请输入 SiliconFlow API Key")

    api_input = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-xxxxxxxxxxxxxxxx",
        key="api_key_input"
    )

    if st.button("保存并启动", type="primary"):
        if validate_api_key(api_input):
            st.session_state.api_key = api_input
            st.success("API Key 已保存")
            time.sleep(1)
            st.rerun()
        else:
            st.error("API Key 格式无效")

    st.stop()


# ================= 主界面 =================

st.title("🩸 VIGIL AETERNUS · 永恒守望者")

col1, col2, col3 = st.columns([1, 1.2, 1])

# ========== 左侧：语音 ==========
with col1:
    st.subheader("🎙 语音输入")

    try:
        from streamlit_mic_recorder import mic_recorder

        audio = mic_recorder(
            start_prompt="开始录音",
            stop_prompt="停止录音",
            just_once=True
        )

        if audio and audio.get("bytes"):
            with st.spinner("转录中..."):
                result = transcribe_audio(audio["bytes"], api_key)

                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success("转录成功")
                else:
                    st.error(result["error"])

    except ImportError:
        st.warning("未安装 streamlit-mic-recorder")

    st.divider()

    uploaded = st.file_uploader(
        "或上传音频文件",
        type=["mp3", "wav", "m4a", "webm"]
    )

    if uploaded:
        if st.button("开始转录"):
            with st.spinner("转录中..."):
                result = transcribe_audio(uploaded.read(), api_key)

                if result["success"]:
                    st.session_state.transcribed_text = result["text"]
                    st.success("转录成功")
                else:
                    st.error(result["error"])


# ========== 中间：编辑 ==========
with col2:
    st.subheader("✍ 编辑内容")

    content = st.text_area(
        "原始文本",
        value=st.session_state.get("transcribed_text", ""),
        height=300
    )

    briefing_type = st.selectbox(
        "生成类型",
        ["会议纪要", "工作日报", "学习笔记", "新闻摘要"],
        index=0
    )

    custom_req = st.text_input("额外要求（可选）")

    if st.button("✨ 生成简报", type="primary", use_container_width=True):
        if not content.strip():
            st.error("请输入内容")
        else:
            with st.spinner("生成中..."):
                result = generate_briefing(
                    content,
                    briefing_type,
                    custom_req,
                    api_key
                )

                if result["success"]:
                    st.session_state.generated = result["text"]
                else:
                    st.error(result["error"])


# ========== 右侧：输出 ==========
with col3:
    st.subheader("📜 输出结果")

    if "generated" in st.session_state:
        result_text = st.session_state.generated

        st.text_area(
            "生成结果",
            value=result_text,
            height=400
        )

        st.download_button(
            "下载为 TXT",
            result_text,
            file_name=f"{briefing_type}_{time.strftime('%Y%m%d_%H%M')}.txt"
        )
    else:
        st.info("等待生成结果...")

# ================= 底部 =================
st.caption("V2.2 安全增强版 · SiliconFlow + DeepSeek")
