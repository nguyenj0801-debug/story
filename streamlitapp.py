import streamlit as st
import os
import re

# ==========================================
# CẤU HÌNH TRANG VÀ CSS
# ==========================================
st.set_page_config(page_title="Trang Đọc Truyện", page_icon="📖", layout="centered")

# CSS tối ưu cho mobile và mắt (chế độ Sepia dịu mắt)
custom_css = """
<style>
    /* Nền và font chữ cho khung đọc truyện */
    .reading-pane {
        background-color: #f4ecd8; /* Màu vàng nhạt (sepia) dịu mắt */
        color: #333333;
        padding: 20px;
        border-radius: 10px;
        font-size: 18px;
        line-height: 1.6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    /* Ẩn bớt padding thừa của Streamlit trên mobile */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Tùy chỉnh thanh tiến trình */
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# CÁC HÀM XỬ LÝ DỮ LIỆU
# ==========================================
BASE_DIR = "./truyen/"

def parse_metadata(novel_dir):
    """Đọc file 000.txt để lấy thông tin truyện."""
    meta_path = os.path.join(novel_dir, "000.txt")
    metadata = {
        "Tên truyện": os.path.basename(novel_dir),
        "Tác giả": "Đang cập nhật",
        "Link": "",
        "Tổng số chương": 0,
        "Đã đọc": 0
    }
    
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if key in ["Tổng số chương", "Đã đọc"]:
                        metadata[key] = int(val) if val.isdigit() else 0
                    else:
                        metadata[key] = val
    return metadata

def update_metadata(novel_dir, metadata, current_chapter_index):
    """Cập nhật lại tiến độ đọc vào file 000.txt."""
    meta_path = os.path.join(novel_dir, "000.txt")
    metadata["Đã đọc"] = current_chapter_index
    
    content = (
        f"Tên truyện: {metadata.get('Tên truyện', '')}\n"
        f"Tác giả: {metadata.get('Tác giả', '')}\n"
        f"Link: {metadata.get('Link', '')}\n"
        f"Tổng số chương: {metadata.get('Tổng số chương', 0)}\n"
        f"Đã đọc: {metadata.get('Đã đọc', 0)}\n"
    )
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(content)

def get_chapters(novel_dir):
    """Lấy danh sách các chapter (loại bỏ 000.txt) và sắp xếp."""
    chapters = []
    if os.path.exists(novel_dir):
        for f in os.listdir(novel_dir):
            if f.endswith(".txt") and f != "000.txt":
                chapters.append(f)
    
    # Sắp xếp theo số ở đầu tên file
    chapters.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    return chapters

def get_all_novels():
    """Quét thư mục gốc để lấy danh sách truyện."""
    novels = []
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path):
            novels.append(item)
    return novels

# ==========================================
# QUẢN LÝ TRẠNG THÁI (SESSION STATE)
# ==========================================
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home' # 'home' hoặc 'reading'
if 'selected_novel' not in st.session_state:
    st.session_state.selected_novel = None
if 'selected_chapter' not in st.session_state:
    st.session_state.selected_chapter = None

# ==========================================
# GIAO DIỆN THANH BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("📚 Điều Hướng")
    
    # Nút về trang chủ
    if st.button("🏠 Về Trang Chủ", use_container_width=True):
        st.session_state.current_view = 'home'
        st.session_state.selected_novel = None
        st.rerun()
        
    st.divider()
    
    # Chức năng tìm kiếm
    search_kw = st.text_input("🔍 Tìm kiếm truyện (Tên/Tác giả):")
    
    # Chức năng chọn truyện từ Sidebar
    all_novels = get_all_novels()
    if all_novels:
        novel_display_names = [parse_metadata(os.path.join(BASE_DIR, n))['Tên truyện'] for n in all_novels]
        novel_dict = dict(zip(novel_display_names, all_novels))
        
        selected_novel_name = st.selectbox(
            "📖 Chuyển Truyện:", 
            options=["-- Chọn truyện --"] + novel_display_names,
            index=0 if st.session_state.selected_novel is None else novel_display_names.index(parse_metadata(os.path.join(BASE_DIR, st.session_state.selected_novel))['Tên truyện']) + 1
        )
        
        if selected_novel_name != "-- Chọn truyện --":
            actual_novel_dir = novel_dict[selected_novel_name]
            if st.session_state.selected_novel != actual_novel_dir:
                st.session_state.selected_novel = actual_novel_dir
                st.session_state.current_view = 'reading'
                # Mở truyện lên thì tự động nhảy đến chapter đang đọc dở
                meta = parse_metadata(os.path.join(BASE_DIR, actual_novel_dir))
                chapters = get_chapters(os.path.join(BASE_DIR, actual_novel_dir))
                if chapters:
                    idx = min(meta['Đã đọc'], len(chapters) - 1)
                    st.session_state.selected_chapter = chapters[idx]
                st.rerun()
                
    # Chức năng chọn chương (Chỉ hiện khi đang ở trong một truyện)
    if st.session_state.selected_novel:
        novel_path = os.path.join(BASE_DIR, st.session_state.selected_novel)
        chapters = get_chapters(novel_path)
        if chapters:
            chapter_idx = 0
            if st.session_state.selected_chapter in chapters:
                chapter_idx = chapters.index(st.session_state.selected_chapter)
                
            selected_chap = st.selectbox(
                "🔖 Chọn Chương:", 
                options=chapters,
                index=chapter_idx
            )
            
            if selected_chap != st.session_state.selected_chapter:
                st.session_state.selected_chapter = selected_chap
                # Cập nhật metadata khi đổi chương
                meta = parse_metadata(novel_path)
                update_metadata(novel_path, meta, chapters.index(selected_chap))
                st.session_state.current_view = 'reading'
                st.rerun()

# ==========================================
# GIAO DIỆN CHÍNH
# ==========================================
if st.session_state.current_view == 'home':
    st.title("Trang Chủ Truyện 📖")
    
    all_nvs = get_all_novels()
    if not all_nvs:
        st.warning(f"Chưa có truyện nào! Hãy tạo thư mục truyện theo cấu trúc trong '{BASE_DIR}'.")
    else:
        # Xử lý tìm kiếm
        display_list = []
        for nv in all_nvs:
            meta = parse_metadata(os.path.join(BASE_DIR, nv))
            if search_kw.lower() in meta['Tên truyện'].lower() or search_kw.lower() in meta['Tác giả'].lower():
                display_list.append((nv, meta))
        
        if not display_list:
            st.info("Không tìm thấy truyện phù hợp với từ khóa.")
            
        # Hiển thị danh sách truyện
        for nv_dir, meta in display_list:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(meta['Tên truyện'])
                    st.caption(f"Tác giả: {meta['Tác giả']} | Nguồn: {meta['Link']}")
                    
                    total = meta['Tổng số chương']
                    read = meta['Đã đọc']
                    progress = read / total if total > 0 else 0
                    st.progress(progress, text=f"Tiến độ: Chương {read} / {total}")
                    
                with col2:
                    st.write("") # Spacer
                    if st.button("Đọc Tiếp", key=f"btn_{nv_dir}", use_container_width=True):
                        st.session_state.selected_novel = nv_dir
                        chapters = get_chapters(os.path.join(BASE_DIR, nv_dir))
                        if chapters:
                            idx = min(read, len(chapters) - 1)
                            st.session_state.selected_chapter = chapters[idx]
                        st.session_state.current_view = 'reading'
                        st.rerun()

elif st.session_state.current_view == 'reading' and st.session_state.selected_novel:
    novel_path = os.path.join(BASE_DIR, st.session_state.selected_novel)
    meta = parse_metadata(novel_path)
    chapters = get_chapters(novel_path)
    
    st.title(meta['Tên truyện'])
    
    if not chapters:
        st.warning("Truyện này hiện chưa có chương nào (hoặc thiếu file txt).")
    else:
        if not st.session_state.selected_chapter:
            st.session_state.selected_chapter = chapters[0]
            
        current_idx = chapters.index(st.session_state.selected_chapter)
        chapter_name = st.session_state.selected_chapter.replace(".txt", "")
        
        st.markdown(f"### {chapter_name}")
        
        # Đọc nội dung file
        chap_path = os.path.join(novel_path, st.session_state.selected_chapter)
        try:
            with open(chap_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Bọc nội dung bằng HTML div chứa class CSS ta đã tạo
            formatted_content = content.replace("\n", "<br>")
            st.markdown(f'<div class="reading-pane">{formatted_content}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Lỗi khi đọc file: {e}")
            
        # Nút chuyển trang (Previous / Next)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if current_idx > 0:
                if st.button("⬅️ Chương Trước", use_container_width=True):
                    st.session_state.selected_chapter = chapters[current_idx - 1]
                    update_metadata(novel_path, meta, current_idx - 1)
                    st.rerun()
        with col3:
            if current_idx < len(chapters) - 1:
                if st.button("Chương Sau ➡️", use_container_width=True):
                    st.session_state.selected_chapter = chapters[current_idx + 1]
                    update_metadata(novel_path, meta, current_idx + 1)
                    st.rerun()
