import streamlit as st
import os
from pathlib import Path
import re

# ====================== CẤU HÌNH PAGE (TỐI ƯU MOBILE) ======================
st.set_page_config(
    page_title="📖 Truyện Hay - Đọc Truyện Mobile",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",   # Tự động thu gọn sidebar trên điện thoại
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Trang đọc truyện tốt nhất trên mobile • Update chapter qua file TXT"
    }
)

# ====================== CUSTOM CSS SIÊU ĐẸP & TỐI ƯU MOBILE ======================
st.markdown('''
<style>
    /* Ẩn header/footer mặc định của Streamlit → immersive reading */
    header, #MainMenu, footer {visibility: hidden;}
    
    /* Container chính gọn gàng, phù hợp màn hình điện thoại */
    .main .block-container {
        padding-top: 0.8rem;
        padding-bottom: 6rem;
        max-width: 720px;
        margin: 0 auto;
    }
    
    /* Tiêu đề chapter */
    .chapter-title {
        font-size: 1.65rem;
        font-weight: 700;
        text-align: center;
        margin: 1.5rem 0 2rem 0;
        color: #ffd700;
    }
    
    /* Nội dung truyện - font đẹp, line-height thoải mái */
    .reading-content {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        text-align: justify;
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        line-height: 1.85;
    }
    
    /* Nút điều hướng to, dễ bấm bằng ngón tay */
    .stButton button {
        height: 52px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 12px;
    }
    
    /* Progress bar đẹp */
    .stProgress > div > div > div > div {
        background-color: #10b981;
    }
    
    /* Responsive cho điện thoại */
    @media (max-width: 768px) {
        .chapter-title {font-size: 1.45rem;}
        .reading-content {padding: 1.4rem 1.1rem; font-size: 1.05rem;}
    }
</style>
''', unsafe_allow_html=True)

# ====================== HÀM HỖ TRỢ ======================
def natural_sort_key(filename: str):
    """Sắp xếp chapter theo số tự nhiên (001, 002, 010...)"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

def get_chapters(folder_path: str):
    path = Path(folder_path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return []
    
    files = [f for f in path.glob("*.txt")]
    # Sắp xếp theo số chapter
    files.sort(key=lambda x: natural_sort_key(x.name))
    return files

# ====================== SESSION STATE ======================
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "font_size" not in st.session_state:
    st.session_state.font_size = 19
if "line_height" not in st.session_state:
    st.session_state.line_height = 1.85
if "theme" not in st.session_state:
    st.session_state.theme = "Tối"

# ====================== SIDEBAR (Cài đặt + Danh sách chapter) ======================
with st.sidebar:
    st.title("📚 Truyện Hay")
    
    # Chọn thư mục chapters (mặc định là ./chapters)
    folder_path = st.text_input("📁 Thư mục chapters", value="./chapters", help="Bạn có thể thay đổi đường dẫn nếu muốn")
    
    chapters = get_chapters(folder_path)
    chapter_titles = [f.stem.replace("_", " ").replace("-", " ").title() for f in chapters]
    
    if chapters:
        # Chọn chapter bằng selectbox (rất mượt trên mobile)
        selected = st.selectbox(
            "Chọn chapter",
            chapter_titles,
            index=st.session_state.current_idx
        )
        new_idx = chapter_titles.index(selected)
        if new_idx != st.session_state.current_idx:
            st.session_state.current_idx = new_idx
            st.rerun()
    
    st.divider()
    st.subheader("⚙️ Cài đặt đọc")
    
    # Điều chỉnh cỡ chữ & khoảng cách dòng
    st.session_state.font_size = st.slider("Cỡ chữ", 14, 30, st.session_state.font_size, step=1)
    st.session_state.line_height = st.slider("Khoảng cách dòng", 1.4, 2.6, st.session_state.line_height, step=0.05)
    
    # Chế độ nền (3 mode phổ biến cho đọc truyện)
    st.session_state.theme = st.selectbox(
        "Chế độ nền",
        ["Tối", "Sepia", "Sáng"],
        index=0
    )

# ====================== MAIN CONTENT ======================
st.title("📖 Truyện Hay")
st.caption("📱 Tối ưu hoàn hảo cho điện thoại • Update chapter chỉ cần thả file TXT")

if not chapters:
    st.info("📂 Chưa có chapter nào!\n\n"
            "**Cách update truyện:**\n"
            "1. Tạo thư mục `chapters` (hoặc đường dẫn bạn vừa nhập)\n"
            "2. Đặt từng file TXT vào (ví dụ: `001.txt`, `002 - Tên chương.txt`...)\n"
            "3. App sẽ tự động sắp xếp và hiển thị!")
    st.stop()

# Lấy chapter hiện tại
current_file = chapters[st.session_state.current_idx]
chapter_name = chapter_titles[st.session_state.current_idx]

# Tiêu đề chapter
st.markdown(f"<div class='chapter-title'>Chương {st.session_state.current_idx + 1}: {chapter_name}</div>", unsafe_allow_html=True)

# Chọn màu nền theo theme
if st.session_state.theme == "Sepia":
    bg_color = "#f5e8c7"
    text_color = "#3c2f1e"
elif st.session_state.theme == "Sáng":
    bg_color = "#f8f9fa"
    text_color = "#1a1a1a"
else:  # Tối
    bg_color = "#1e1e1e"
    text_color = "#e0e0e0"

# Đọc nội dung file TXT
content = current_file.read_text(encoding="utf-8")

# Hiển thị nội dung với style động
styled_content = f"""
<div class="reading-content" style="
    font-size: {st.session_state.font_size}px; 
    line-height: {st.session_state.line_height};
    background-color: {bg_color};
    color: {text_color};
">
{content.replace("\n\n", "</p><p>").replace("\n", "<br>")}
</div>
"""
st.markdown(styled_content, unsafe_allow_html=True)

# Progress bar
progress = (st.session_state.current_idx + 1) / len(chapters)
st.progress(progress, text=f"Đã đọc {st.session_state.current_idx + 1}/{len(chapters)} chapter")

# ====================== NAVIGATION (TOP + BOTTOM) ======================
# Top navigation
col1, col2, col3 = st.columns([1, 3, 1])
with col1:
    if st.button("← Trước", use_container_width=True) and st.session_state.current_idx > 0:
        st.session_state.current_idx -= 1
        st.rerun()
with col2:
    st.empty()  # giữ khoảng trống để cân đối
with col3:
    if st.button("Sau →", use_container_width=True) and st.session_state.current_idx < len(chapters) - 1:
        st.session_state.current_idx += 1
        st.rerun()

# Bottom navigation (dễ bấm hơn trên mobile)
st.markdown("---")
bc1, bc2, bc3 = st.columns([1, 2, 1])
with bc1:
    if st.button("⬅️ Chương trước", use_container_width=True) and st.session_state.current_idx > 0:
        st.session_state.current_idx -= 1
        st.rerun()
with bc2:
    st.caption(f"📖 {chapter_name}")
with bc3:
    if st.button("Chương sau ➡️", use_container_width=True) and st.session_state.current_idx < len(chapters) - 1:
        st.session_state.current_idx += 1
        st.rerun()

# ====================== HƯỚNG DẪN SỬ DỤNG ======================
st.caption("💡 Mẹo: Vuốt lên/xuống để đọc, dùng nút ☰ bên trái để chọn chapter nhanh. App chạy mượt trên mọi điện thoại!")
