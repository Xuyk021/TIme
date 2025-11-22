import streamlit as st
import time
import random

st.title('Where should we begin?')
user_input = st.chat_input('Enter your question')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# 先把历史消息画出来（只用最终的 content）
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)


mode = st.sidebar.radio(
    "Response mode",
    [
        "No thinking",
        "No Cues (custom)",
        "Thinking (fixed 2s)",
        "Thinking (custom)",
    ],
)
thinking_enabled = mode != "No thinking"


# 默认的 thinking_time
thinking_time = 0.0
if mode == "Thinking (fixed 2s)":
    thinking_time = 2.0
elif mode == "Thinking (custom)":
    thinking_time = st.sidebar.slider(
        "Thinking time (seconds)",
        min_value=2.0,
        max_value=35.0,
        value=3.0,
        step=0.5,
    )
elif mode == "No Cues (custom)":
    thinking_time = st.sidebar.slider(
        "Thinking time (seconds)",
        min_value=0.0,
        max_value=35.0,
        value=3.0,
        step=0.5,
    )

st.sidebar.markdown("---")
st.sidebar.write(f"Thinking enabled: **{thinking_enabled}**")
if thinking_enabled:
    st.sidebar.write(f"Thinking time: **{thinking_time} s**")

if st.sidebar.button("Clear chat history", type="primary"):
    st.session_state.messages = []      # 清空记录
    st.rerun()                           # 立即刷新（防止旧记录残留）

    
# 答案池
answers = [
    "Raw milk and pasteurized milk have very similar nutritional profiles. Pasteurization does not significantly reduce macronutrients like protein, fat, or carbohydrates. Some heat-sensitive vitamins may decrease slightly, but the differences are small. The major distinction is safety: pasteurized milk greatly reduces the risk of harmful bacteria, while raw milk carries higher risk without providing meaningful nutritional advantages.",
    "Raw milk is not substantially more nutritious than pasteurized milk. Their vitamin, mineral, and protein levels are nearly the same. Pasteurization mainly targets pathogens and has minimal impact on overall nutrition. The primary trade-off is that raw milk may preserve a small amount of heat-sensitive enzymes, but these do not provide proven health benefits, while the safety risks are well documented.",
    "There is no strong scientific evidence that raw milk offers superior nutrition compared to pasteurized milk. Pasteurization keeps the main nutrients intact and only slightly reduces certain vitamins that are naturally unstable. The key difference lies in microbial safety, not nutritional value. Pasteurized milk is considered much safer to drink without sacrificing meaningful nutritional quality."
]

def get_random_answer():
    return random.choice(answers)

# 在同一个 placeholder 里展示 Thinking + 最终答案（没有多余元素）
def think_and_stream(placeholder, answer_text, delay_seconds=1.0, display=None, mode=None):
    # 1) Thinking 动画
    gray_scale = ["#cccccc", "#bfbfbf", "#b3b3b3", "#a6a6a6", "#999999",
                  "#8c8c8c", "#808080", "#8c8c8c", "#999999", "#a6a6a6",
                  "#b3b3b3", "#bfbfbf"]

    start = time.time()
    idx = 0

    # 防止 display=None 的情况
    if display and mode != "No Cues (custom)":
        while True:
            elapsed = time.time() - start
            if elapsed >= delay_seconds:
                break
            color = gray_scale[idx % len(gray_scale)]
            idx += 1
            placeholder.markdown(
                f"<span style='color:{color}; font-style:italic;'>Thinking for {elapsed:.1f} s</span>",
                unsafe_allow_html=True
            )
            time.sleep(0.1)

        # 这里固定一条最终的 Thought 文本，后面流式输出时一直带着它
        thought_header = (
            f"<div style='color:#999; font-style:italic; margin-bottom:10px;'>"
            f"Thought for {delay_seconds:.1f} s"
            f"</div>"
        )
    elif mode == "No Cues (custom)":
        thought_header = ""
        time.sleep(delay_seconds)
    else:
        thought_header = ""

    time.sleep(0.3)

    # 2) 流式输出：每次都在前面加上 thought_header，这样它不会被覆盖
    accumulated = ""
    for word in answer_text.split():
        accumulated += word + " "
        placeholder.markdown(thought_header + accumulated, unsafe_allow_html=True)
        time.sleep(0.03)

    # 把包含 Thought header 的完整 HTML 返回，方便存到 history
    return thought_header + accumulated

def question_check(user_input):
    # 简单示例：检查问题是否以问号结尾
    if not user_input == 'Is raw milk more nutritious than pasteurized milk?':
        st.warning("Please ask a question related to milk nutrition.")
        return False
    else:
        return True

if user_input:
    # 用户消息
    with st.chat_message("User_A", avatar=None):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "User_A", "content": user_input})

    if question_check(user_input):
        
        # AI 消息
        with st.chat_message("AI_A"):
            msg_placeholder = st.empty()       # 整个气泡里只用这一个 placeholder
            full_answer = get_random_answer()
            final_text = think_and_stream(msg_placeholder, full_answer, delay_seconds=thinking_time, display=thinking_enabled, mode=mode)

        # 只把最终文本写进 history
        st.session_state.messages.append({"role": "AI_A", "content": final_text})
