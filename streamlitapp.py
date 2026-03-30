import streamlit as st
from pathlib import Path
import re
import os

# ====================== CẤU HÌNH PAGE ======================
st.set_page_config(
    page_title="📚 Thư Viện Truyện Hay",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",   # Thu gọn sidebar trên mobile
)

# ====================== CUSTOM CSS (TỐI ƯU MOBILE) ======================
st.markdown('''
<style>
    header, #MainMenu, footer {visibility: hidden;}
    
    .main .block-container {
        padding-top: 0.5rem;
        padding-bottom: 6rem;
        max-width: 720px;
        margin: 0 auto;
    }
    
    .book-title {
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        color: #ffd700;
        margin: 1rem 0;
    }
    
    .chapter-title {
        font-size: 1.55rem;
        font-weight: 700;
        text-align: center;
        margin: 1.8rem 0 2rem 0;
        color: #ffd700;
    }
    
    .reading-content {
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        text-align: justify;
        padding: 1.8rem 1.5rem;
        border-radius: 16px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
        line-height: 1.85;
        font-size: 1.05rem;
    }
    
    .stButton button {
        height: 54px;
        font-size: 1.15rem;
        font-weight: 600;
        border-radius: 12px;
    }
    
    @media (max-width: 768px) {
        .book-title {font-size: 1.55rem;}
        .chapter-title {font-size: 1.4rem;}
        .reading-content {padding: 1.4rem 1.1rem; font-size: 1.08rem;}
    }
</style>
''', unsafe_allow_html=True)

# ====================== HÀM HỖ TRỢ ======================
def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def get_books(base_path: Path):
    """Lấy danh sách các thư mục (mỗi thư mục là 1 truyện)"""
    if not base_path.exists():
        base_path.mkdir(parents=True, exist_ok=True)
    books = [d for d in base_path.iterdir() if d.is_dir()]
    books.sort(key=lambda x: x.name.lower())
    return books

def get_chapters(book_path: Path):
    """Lấy danh sách chapter trong thư mục truyện"""
    files = list(book_path.glob("*.txt"))
    files.sort(key=lambda x: natural_sort_key(x.stem))
    return files

# ====================== SESSION STATE ======================
if "current_book_idx" not in st.session_state:
    st.session_state.current_book_idx = 0
if "current_chapter_idx" not in st.session_state:
    st.session_state.current_chapter_idx = 0
if "font_size" not in st.session_state:
    st.session_state.font_size = 19
if "line_height" not in st.session_state:
    st.session_state.line_height = 1.85
if "theme" not in st.session_state:
    st.session_state.theme = "Tối"

# ====================== SIDEBAR ======================
with st.sidebar:
    st.title("📚 Thư Viện Truyện")
    
    base_folder = st.text_input("📁 Thư mục gốc chứa các truyện", value="./truyen", help="Mỗi thư mục con bên trong là một truyện")
    base_path = Path(base_folder)
    
    books = get_books(base_path)
    book_names = [book.name for book in books]
    
    if books:
        # Chọn truyện
        selected_book = st.selectbox("Chọn truyện", book_names, index=st.session_state.current_book_idx)
        new_book_idx = book_names.index(selected_book)
        
        if new_book_idx != st.session_state.current_book_idx:
            st.session_state.current_book_idx = new_book_idx
            st.session_state.current_chapter_idx = 0  # Reset về chapter 1 khi đổi truyện
            st.rerun()
        
        current_book_path = books[st.session_state.current_book_idx]
        chapters = get_chapters(current_book_path)
        chapter_titles = [f.stem.replace("_", " ").replace("-", " ").title() for f in chapters]
        
        if chapters:
            selected_chapter = st.selectbox("Chọn chapter", chapter_titles, index=st.session_state.current_chapter_idx)
            new_chapter_idx = chapter_titles.index(selected_chapter)
            if new_chapter_idx != st.session_state.current_chapter_idx:
                st.session_state.current_chapter_idx = new_chapter_idx
                st.rerun()
        
        st.divider()
        st.subheader("⚙️ Cài đặt đọc")
        st.session_state.font_size = st.slider("Cỡ chữ", 14, 32, st.session_state.font_size, 1)
        st.session_state.line_height = st.slider("Khoảng cách dòng", 1.4, 2.6, st.session_state.line_height, 0.05)
        st.session_state.theme = st.selectbox("Chế độ nền", ["Tối", "Sepia", "Sáng"], index=0)
    else:
        st.warning("Chưa có truyện nào. Hãy tạo thư mục con bên trong `./truyen` và thả file .txt vào.")

# ====================== MAIN CONTENT ======================
st.title("📖 Thư Viện Truyện Hay")
st.caption("📱 Tối ưu cho điện thoại • Mỗi thư mục = 1 truyện")

if not books:
    st.info(f"""
    **Hướng dẫn sử dụng:**
    1. Tạo thư mục `{base_folder}` (hoặc đường dẫn bạn nhập)
    2. Bên trong tạo từng thư mục con, ví dụ:
       - `Dau_Pha_Thien_Khung`
       - `Bach_Luyen_Thanh_Than`
       - `Ngich_Thien_Tu_Hanh`
    3. Mỗi thư mục con chứa các file `001.txt`, `002.txt`, `003 - Tên chương.txt`...
    4. App sẽ tự động nhận và sắp xếp chapter!
    """)
    st.stop()

# Lấy dữ liệu hiện tại
current_book_path = books[st.session_state.current_book_idx]
current_book_name = book_names[st.session_state.current_book_idx]
chapters = get_chapters(current_book_path)

if not chapters:
    st.warning(f"Truyện **{current_book_name}** chưa có chapter nào. Hãy thêm file .txt vào thư mục này.")
    st.stop()

current_chapter_file = chapters[st.session_state.current_chapter_idx]
chapter_name = chapter_titles[st.session_state.current_chapter_idx]

# Tiêu đề truyện và chapter
st.markdown(f"<div class='book-title'>{current_book_name.replace('_', ' ').replace('-', ' ').title()}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='chapter-title'>Chương {st.session_state.current_chapter_idx + 1}: {chapter_name}</div>", unsafe_allow_html=True)

# Chọn màu nền theo theme
if st.session_state.theme == "Sepia":
    bg = "#f5e8c7"
    color = "#3c2f1e"
elif st.session_state.theme == "Sáng":
    bg = "#f8f9fa"
    color = "#1a1a1a"
else:
    bg = "#1e1e1e"
    color = "#e0e0e0"

# Đọc nội dung chapter
content = current_chapter_file.read_text(encoding="utf-8")

# Hiển thị nội dung
styled_content = f"""
<div class="reading-content" style="
    font-size: {st.session_state.font_size}px; 
    line-height: {st.session_state.line_height};
    background-color: {bg};
    color: {color};
">
{content.replace("\n\n", "</p><p>").replace("\n", "<br>")}
</div>
"""
st.markdown(styled_content, unsafe_allow_html=True)

# Progress
progress = (st.session_state.current_chapter_idx + 1) / len(chapters)
st.progress(progress, text=f"Chapter {st.session_state.current_chapter_idx + 1}/{len(chapters)}")

# ====================== NAVIGATION ======================
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("← Chương trước", use_container_width=True) and st.session_state.current_chapter_idx > 0:
        st.session_state.current_chapter_idx -= 1
        st.rerun()
with col3:
    if st.button("Chương sau →", use_container_width=True) and st.session_state.current_chapter_idx < len(chapters) - 1:
        st.session_state.current_chapter_idx += 1
        st.rerun()

st.markdown("---")
st.caption("💡 Mẹo: Dùng menu bên trái để chuyển truyện hoặc chapter nhanh. Thêm file TXT mới vào thư mục là app tự cập nhật!")
