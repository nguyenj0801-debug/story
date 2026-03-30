import streamlit as st
import os
import re

# ==========================================
# CẤU HÌNH TRANG VÀ CSS (CHO GIAO DIỆN STREAMLIT)
# ==========================================
st.set_page_config(page_title="Trang Đọc Truyện", page_icon="📖", layout="centered")

custom_css = """
<style>
    .reading-pane {
        background-color: #f4ecd8;
        color: #333333;
        padding: 20px;
        border-radius: 10px;
        font-size: 18px;
        line-height: 1.6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# CÁC HÀM XỬ LÝ DỮ LIỆU
# ==========================================
BASE_DIR = "./truyen/"

def parse_metadata(novel_dir):
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
    chapters = []
    if os.path.exists(novel_dir):
        for f in os.listdir(novel_dir):
            if f.endswith(".txt") and f != "000.txt":
                chapters.append(f)
    chapters.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    return chapters

def get_all_novels():
    novels = []
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if os.path.isdir(item_path):
            novels.append(item)
    return novels

# ==========================================
# HÀM TẠO FILE HTML OFFLINE CHỨA JS/CSS
# ==========================================
def generate_offline_html(novel_path, meta, chapters):
    novel_title = meta['Tên truyện']
    
    # CSS và JS cho bản offline (Lưu ý: dùng {{ và }} để escape dấu ngoặc nhọn trong f-string)
    html_head = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{novel_title} - Offline</title>
    <style>
        body {{
            background-color: #f4ecd8; /* Sepia dịu mắt */
            color: #333333;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            font-size: 18px;
            line-height: 1.6;
            padding: 15px;
            max-width: 800px;
            margin: auto;
        }}
        h1, h2 {{ text-align: center; color: #2c3e50; }}
        .nav-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 20px 0;
            padding: 10px;
            background: rgba(0,0,0,0.05);
            border-radius: 8px;
        }}
        button, select {{
            padding: 10px 15px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }}
        button:disabled {{ background-color: #ccc; cursor: not-allowed; }}
        select {{ background-color: #fff; color: #333; border: 1px solid #ccc; max-width: 50%; }}
        .chapter-content {{ display: none; margin-bottom: 40px; }}
        .active-chapter {{ display: block; }}
    </style>
</head>
<body>
    <h1>{novel_title}</h1>
    
    <div class="nav-container">
        <button id="btn-prev-top" onclick="changeChapter(-1)">⬅️ Trước</button>
        <select id="chap-select-top" onchange="jumpToChapter(this.value)"></select>
        <button id="btn-next-top" onclick="changeChapter(1)">Sau ➡️</button>
    </div>
    
    <div id="content-area">
"""
    
    html_body = ""
    chap_options = ""
    
    # Đọc nội dung từng file và đưa vào các thẻ div ẩn
    for idx, chap_file in enumerate(chapters):
        chap_path = os.path.join(novel_path, chap_file)
        chap_name = chap_file.replace(".txt", "")
        chap_options += f'<option value="{idx}">{chap_name}</option>\n'
        
        try:
            with open(chap_path, "r", encoding="utf-8") as f:
                content = f.read().replace("\n", "<br>")
        except Exception:
            content = "Lỗi đọc file."
            
        html_body += f"""
        <div id="chap-{idx}" class="chapter-content">
            <h2>{chap_name}</h2>
            <div>{content}</div>
        </div>
        """
        
    html_tail = f"""
    </div>

    <div class="nav-container">
        <button id="btn-prev-bottom" onclick="changeChapter(-1)">⬅️ Trước</button>
        <select id="chap-select-bottom" onchange="jumpToChapter(this.value)">
            {chap_options}
        </select>
        <button id="btn-next-bottom" onclick="changeChapter(1)">Sau ➡️</button>
    </div>

    <script>
        const totalChapters = {len(chapters)};
        let currentIdx = 0;

        function updateUI() {{
            // Ẩn tất cả, chỉ hiện chương hiện tại
            document.querySelectorAll('.chapter-content').forEach(el => el.classList.remove('active-chapter'));
            document.getElementById('chap-' + currentIdx).classList.add('active-chapter');
            
            // Đồng bộ dropdown
            document.getElementById('chap-select-top').value = currentIdx;
            document.getElementById('chap-select-bottom').value = currentIdx;
            
            // Cập nhật trạng thái nút bấm
            const isFirst = (currentIdx === 0);
            const isLast = (currentIdx === totalChapters - 1);
            
            document.getElementById('btn-prev-top').disabled = isFirst;
            document.getElementById('btn-prev-bottom').disabled = isFirst;
            document.getElementById('btn-next-top').disabled = isLast;
            document.getElementById('btn-next-bottom').disabled = isLast;
            
            // Cuộn lên đầu trang khi đổi chương
            window.scrollTo(0, 0);
        }}

        function changeChapter(step) {{
            const newIdx = currentIdx + step;
            if(newIdx >= 0 && newIdx < totalChapters) {{
                currentIdx = newIdx;
                updateUI();
            }}
        }}

        function jumpToChapter(idxStr) {{
            currentIdx = parseInt(idxStr);
            updateUI();
        }}

        // Khởi tạo
        window.onload = () => {{
            // Copy options từ dưới lên trên
            document.getElementById('chap-select-top').innerHTML = document.getElementById('chap-select-bottom').innerHTML;
            updateUI();
        }};
    </script>
</body>
</html>
"""
    return html_head + html_body + html_tail

# ==========================================
# QUẢN LÝ TRẠNG THÁI (SESSION STATE)
# ==========================================
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'home'
if 'selected_novel' not in st.session_state:
    st.session_state.selected_novel = None
if 'selected_chapter' not in st.session_state:
    st.session_state.selected_chapter = None

# ==========================================
# GIAO DIỆN THANH BÊN (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("📚 Điều Hướng")
    if st.button("🏠 Về Trang Chủ", use_container_width=True):
        st.session_state.current_view = 'home'
        st.session_state.selected_novel = None
        st.rerun()
        
    st.divider()
    search_kw = st.text_input("🔍 Tìm kiếm truyện (Tên/Tác giả):")
    
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
                meta = parse_metadata(os.path.join(BASE_DIR, actual_novel_dir))
                chapters = get_chapters(os.path.join(BASE_DIR, actual_novel_dir))
                if chapters:
                    idx = min(meta['Đã đọc'], len(chapters) - 1)
                    st.session_state.selected_chapter = chapters[idx]
                st.rerun()
                
    if st.session_state.selected_novel:
        novel_path = os.path.join(BASE_DIR, st.session_state.selected_novel)
        chapters = get_chapters(novel_path)
        if chapters:
            chapter_idx = chapters.index(st.session_state.selected_chapter) if st.session_state.selected_chapter in chapters else 0
            selected_chap = st.selectbox("🔖 Chọn Chương:", options=chapters, index=chapter_idx)
            if selected_chap != st.session_state.selected_chapter:
                st.session_state.selected_chapter = selected_chap
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
        display_list = []
        for nv in all_nvs:
            meta = parse_metadata(os.path.join(BASE_DIR, nv))
            if search_kw.lower() in meta['Tên truyện'].lower() or search_kw.lower() in meta['Tác giả'].lower():
                display_list.append((nv, meta))
        
        if not display_list:
            st.info("Không tìm thấy truyện phù hợp với từ khóa.")
            
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
                    st.write("") 
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
    
    # Khu vực Tiêu đề và Nút tải Offline
    col_title, col_download = st.columns([3, 1])
    with col_title:
        st.title(meta['Tên truyện'])
    with col_download:
        st.write("") # Căn chỉnh cho đẹp
        if chapters:
            # Tạo nội dung file HTML gộp
            html_content = generate_offline_html(novel_path, meta, chapters)
            # Nút download của Streamlit
            st.download_button(
                label="⬇️ Tải bản Offline (HTML)",
                data=html_content,
                file_name=f"{meta['Tên truyện']}_offline.html",
                mime="text/html",
                use_container_width=True
            )
    
    if not chapters:
        st.warning("Truyện này hiện chưa có chương nào (hoặc thiếu file txt).")
    else:
        if not st.session_state.selected_chapter:
            st.session_state.selected_chapter = chapters[0]
            
        current_idx = chapters.index(st.session_state.selected_chapter)
        chapter_name = st.session_state.selected_chapter.replace(".txt", "")
        
        st.markdown(f"### {chapter_name}")
        
        chap_path = os.path.join(novel_path, st.session_state.selected_chapter)
        try:
            with open(chap_path, "r", encoding="utf-8") as f:
                content = f.read()
            formatted_content = content.replace("\n", "<br>")
            st.markdown(f'<div class="reading-pane">{formatted_content}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Lỗi khi đọc file: {e}")
            
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
