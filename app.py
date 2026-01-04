import streamlit as st
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Jigsaw Solver", page_icon="🧩", layout="wide")

# --- HÀM KIỂM TRA LOẠI THẺ ---
def get_token_type(token):
    if isinstance(token, (int, float)): return "NUM"
    if token in ['+', '-', '*', '/', '^']: return "BIN_OP"
    if token == 'v': return "UNARY_PRE"
    if token == '!': return "UNARY_POST"
    if token == '(': return "OPEN"
    if token == ')': return "CLOSE"
    return "UNKNOWN"

# --- THUẬT TOÁN QUAY LUI (BACKTRACKING) ---
def solve_jigsaw(tokens, target_list, tolerance):
    solutions = []
    seen_expr = set()

    def backtrack(current_expr_list, remaining_tokens, balance, last_type):
        # 1. KẾT THÚC CHUỖI
        if not remaining_tokens:
            # Đóng hết ngoặc & không tận cùng bằng phép tính
            if balance == 0 and last_type in ["NUM", "CLOSE", "UNARY_POST"]:
                
                # Tạo chuỗi hiển thị
                display_str = "".join([str(x) for x in current_expr_list])
                
                if display_str in seen_expr: return
                seen_expr.add(display_str)

                # Tạo chuỗi tính toán (Xử lý Python syntax)
                try:
                    # Chuyển đổi sơ bộ: ^ -> **
                    # Lưu ý: Code này tập trung vào phép tính cơ bản & ngoặc.
                    # Căn (v) và Giai thừa (!) trong chế độ xếp hình tự do rất khó parse
                    # nên ta xử lý đơn giản: thay thế ký tự nếu có thể.
                    
                    py_str = display_str.replace('^', '**')
                    
                    # Trick xử lý căn 'v': thay v thành math.sqrt nhưng phải có ngoặc
                    # Ở đây ta giả định người dùng nhập v(...) hoặc vSố
                    # Nếu quá phức tạp sẽ bỏ qua case lỗi.
                    py_str = py_str.replace('v', 'math.sqrt') 
                    # Lưu ý: math.sqrt5 là lỗi, phải là math.sqrt(5). 
                    # Do đó, người dùng nên nhập 'v' '(' '5' ')' để an toàn nhất.

                    val = eval(py_str)
                    
                    if isinstance(val, complex): return
                    
                    for t in target_list:
                        diff = abs(val - t)
                        # Lưu hết tất cả kết quả nằm trong sai số
                        if diff <= tolerance:
                            solutions.append({
                                'val': val,
                                'expr': display_str,
                                'diff': diff,
                                'target': t
                            })
                except:
                    return
            return

        # 2. CHỌN THẺ TIẾP THEO
        unique_tokens = sorted(list(set(remaining_tokens)), key=str)
        
        for token in unique_tokens:
            t_type = get_token_type(token)
            is_valid = False
            
            # --- CHECK NGỮ PHÁP (Grammar Rules) ---
            if last_type == "START":
                if t_type in ["NUM", "OPEN", "UNARY_PRE"]: is_valid = True
            elif last_type == "NUM":
                if t_type in ["BIN_OP", "CLOSE", "UNARY_POST"]: is_valid = True
            elif last_type == "BIN_OP":
                if t_type in ["NUM", "OPEN", "UNARY_PRE"]: is_valid = True
            elif last_type == "OPEN":
                if t_type in ["NUM", "OPEN", "UNARY_PRE"]: is_valid = True
            elif last_type == "CLOSE":
                if t_type in ["BIN_OP", "CLOSE", "UNARY_POST"]: is_valid = True
            elif last_type == "UNARY_PRE": # v
                if t_type == "OPEN": is_valid = True # Bắt buộc v(
            elif last_type == "UNARY_POST": # !
                if t_type in ["BIN_OP", "CLOSE"]: is_valid = True

            if t_type == "CLOSE" and balance <= 0: is_valid = False
            
            if is_valid:
                new_tokens = list(remaining_tokens)
                new_tokens.remove(token)
                new_balance = balance + 1 if t_type == "OPEN" else (balance - 1 if t_type == "CLOSE" else balance)
                
                # Cắt nhánh: Nếu không đủ thẻ để đóng ngoặc
                if len(new_tokens) < new_balance: continue

                backtrack(current_expr_list + [token], new_tokens, new_balance, t_type)

    backtrack([], tokens, 0, "START")
    return solutions

# --- GIAO DIỆN CHÍNH ---
st.title("🧩 Solver: Tìm Số Thập Phân Gần Đúng")
st.markdown("""
Công cụ này sẽ sắp xếp các mảnh ghép để tìm ra kết quả **GẦN NHẤT** với mục tiêu (1 và 20).
Nó sẽ ưu tiên hiển thị cả các phép tính ra số lẻ (ví dụ: 1.1, 19.9).
""")

with st.sidebar:
    st.header("Nhập liệu")
    # Mẹo: Thêm phép chia / để dễ ra số thập phân
    nums_in = st.text_input("Các số", "3 5 2 8 1")
    ops_in = st.text_input("Các phép tính", "( ) + / *")
    st.caption("💡 Mẹo: Muốn ra số thập phân, hãy dùng phép chia `/` hoặc căn `v`.")
    
    st.divider()
    # Tăng sai số mặc định lên để dễ tìm thấy kết quả "gần đúng"
    tolerance = st.slider("Sai số cho phép (+/-)", 0.0, 10.0, 2.0, 0.1)
    run_btn = st.button("🚀 Chạy Tìm Kiếm", type="primary")

if run_btn:
    # Xử lý input
    clean_nums = nums_in.replace(',', ' ').split()
    nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
    clean_ops = ops_in.replace(',', ' ').split()
    ops = [x.strip() for x in clean_ops]
    tokens = nums + ops
    
    st.info(f"Đang tìm cách sắp xếp **{len(tokens)} mảnh ghép**: `{tokens}`")

    with st.spinner("Đang tính toán các trường hợp thập phân..."):
        results = solve_jigsaw(tokens, [1, 20], tolerance)
        
        if not results:
            st.warning("Không tìm thấy kết quả nào trong khoảng sai số này.")
        else:
            st.success(f"Tìm thấy {len(results)} phương án!")
            
            c1, c2 = st.columns(2)
            
            def show_detailed_results(target, container):
                subset = [r for r in results if r['target'] == target]
                subset.sort(key=lambda x: x['diff'])
                
                if not subset:
                    container.caption("Không có nghiệm phù hợp.")
                    return
                
                # Lọc trùng lặp biểu thức
                seen = set()
                unique_subset = []
                for x in subset:
                    if x['expr'] not in seen:
                        unique_subset.append(x)
                        seen.add(x['expr'])
                
                # Chia làm 2 nhóm: Chính xác (Diff=0) và Gần đúng (Diff>0)
                exacts = [x for x in unique_subset if x['diff'] < 0.000001]
                approximates = [x for x in unique_subset if x['diff'] >= 0.000001]

                # HIỂN THỊ CHÍNH XÁC
                if exacts:
                    container.markdown(f"##### ✅ Chính xác tuyệt đối ({target})")
                    for item in exacts[:3]:
                        container.code(f"{item['expr']} = {item['val']}", language='text')
                
                # HIỂN THỊ GẦN ĐÚNG (DECIMAL)
                if approximates:
                    container.markdown(f"##### ≈ Các phương án Gần đúng nhất")
                    for item in approximates[:10]: # Lấy top 10 gần nhất
                        
                        # Logic màu: Lệch ít (<0.5) màu xanh, Lệch nhiều màu cam
                        color_code = "#0f5132" if item['diff'] < 0.5 else "#664d03"
                        bg_code = "#d1e7dd" if item['diff'] < 0.5 else "#fff3cd"
                        
                        # Hiển thị dạng Card
                        container.markdown(f"""
                        <div style="background:{bg_code}; padding:8px; border-radius:6px; margin-bottom:6px; border-left: 4px solid {color_code}">
                            <div style="font-size:14px; color:#333; font-family:monospace;">{item['expr']}</div>
                            <div style="display:flex; justify_content:space-between; align-items:center;">
                                <strong style="color:{color_code}; font-size:16px;">= {item['val']:.5f}</strong>
                                <span style="font-size:12px; color:#666;">(Lệch: {item['diff']:.5f})</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                elif not exacts:
                    container.write("Chưa tìm thấy kết quả gần đúng.")

            with c1:
                st.subheader("Mục tiêu ~ 1")
                show_detailed_results(1, c1)
            
            with c2:
                st.subheader("Mục tiêu ~ 20")
                show_detailed_results(20, c2)
