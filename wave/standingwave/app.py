import time

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # 引入字体管理模块
import numpy as np
import streamlit as st
import os

# --- 核心修改 (修正版) ---
# 1. 获取字体路径
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, 'SimHei.ttf')

# 2. 关键一步：使用 addfont 直接把文件注册到 Matplotlib
# 这样 Matplotlib 就知道 "SimHei" 对应这个文件了
fm.fontManager.addfont(font_path)

# 3. 设置全局字体为 SimHei
plt.rcParams['font.family'] = ['SimHei'] 

# 4. 解决负号显示为方块的问题
plt.rcParams['axes.unicode_minus'] = False 
# --- 核心修改结束 ---

st.set_page_config(page_title="驻波演示", layout="wide")
st.title("驻波（Standing Wave）演示")
st.caption("使用两个反向传播的简谐波叠加展示驻波的形成")

# 侧边栏参数控制
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 兼容中文
plt.rcParams["axes.unicode_minus"] = False

st.sidebar.header("参数设置")
amplitude = st.sidebar.slider("振幅 A", min_value=0.1, max_value=2.0, value=1.0, step=0.1)
frequency = st.sidebar.slider("频率 f (Hz)", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
wave_speed = st.sidebar.slider("波速 v (m/s)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)

# 动画开关使用按钮；显式 key 避免状态丢失
if "running" not in st.session_state:
    st.session_state.running = False
if "phase" not in st.session_state:
    st.session_state.phase = 0.0

if st.sidebar.button("播放/暂停", type="primary"):
    st.session_state.running = not st.session_state.running

# 空间范围
x = np.linspace(0, 10, 400)

# 绘图占位符
placeholder = st.empty()

def draw_frame(t: float) -> None:
    """根据当前时间 t 绘制一帧并更新占位符。"""
    omega = 2 * np.pi * frequency
    k = omega / wave_speed

    y1 = amplitude * np.sin(k * (x - wave_speed * t))
    y2 = amplitude * np.sin(k * (x + wave_speed * t))
    y_total = y1 + y2

    # 节点（驻波始终为 0 的位置）出现在 kx = n*pi => x = n*pi/k
    if k != 0:
        node_positions = np.arange(0, k * x[-1] + np.pi, np.pi) / k
        node_positions = node_positions[node_positions <= x[-1]]
    else:
        node_positions = np.array([])
    node_y = np.zeros_like(node_positions)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y1, "b--", linewidth=1, label="波 1（→）")
    ax.plot(x, y2, "r--", linewidth=1, label="波 2（←）")
    ax.plot(x, y_total, "k-", linewidth=2, label="叠加结果：驻波")

    # 标注节点：粗圆点 + x 坐标
    if len(node_positions) > 0:
        ax.plot(node_positions, node_y, "ko", markersize=8, label="节点")
        for xp in node_positions:
            ax.text(xp, 0.15, f"{xp:.2f}", ha="center", va="bottom", fontsize=8, rotation=0)
    ax.set_xlim(0, 10)
    ax.set_ylim(-4, 4)
    ax.set_xlabel("位置 x")
    ax.set_ylabel("位移 y")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle=":", linewidth=0.5)

    placeholder.pyplot(fig)
    plt.close(fig)


# 播放/暂停逻辑：同一 run 内绘制多帧，结束时保持当前形状
dt = 0.05
if not st.session_state.running:
    draw_frame(t=st.session_state.phase)
    st.info("点击左侧“播放/暂停”按钮开始动画。")
else:
    max_steps = 400  # 单次运行最多画 400 帧（约 20s），避免阻塞过久
    for _ in range(max_steps):
        if not st.session_state.get("running", False):
            break
        draw_frame(st.session_state.phase)
        st.session_state.phase += dt
        time.sleep(dt)
    # 退出时保持当前波形，不强制重置 running



