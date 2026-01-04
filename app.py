import streamlit as st
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver: Top 10 Report", page_icon="📊", layout="wide")

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
            if balance == 0 and last_type in ["NUM", "CLOSE", "UNARY_POST"]:
                
                # Tạo chuỗi hiển thị
                display_str = "".join([str(x) for x in current_expr_list])
                
                if display_str in seen_expr: return
                seen_expr.add(display_str)

                # Tạo chuỗi tính toán (Xử lý Python syntax)
                try:
                    py_str = display_str.replace('^', '**')
                    py_str = py_str.replace('v', 'math.sqrt') 

                    val = eval(py_str)
                    
                    if isinstance(val, complex): return
                    
                    for t in target_list:
                        diff = abs(val - t)
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
            
            # CHECK NGỮ PHÁP
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
            elif last_type == "UNARY_PRE": 
                if t_type == "OPEN": is_valid = True 
            elif last_type == "UNARY_POST":
                if t_type in ["BIN_OP", "CLOSE"]: is_valid = True

            if t_type == "CLOSE" and balance <= 0: is_valid = False
            
            if is_valid:
                new_tokens = list(remaining_tokens)
                new_tokens.remove(token)
                new_balance = balance + 1 if t_type == "OPEN" else (balance - 1 if t_type == "CLOSE" else balance)
                
                if len(new_tokens) < new_balance: continue

                backtrack(current_expr_list + [token], new_tokens, new_balance, t_type)

    backtrack([], tokens, 0, "START")
    return solutions

# --- GIAO DIỆN CHÍNH ---
st.title("📊 Báo Cáo Top 10 Phép Tính")
st.markdown("""
Hệ thống sẽ tìm kiếm và xuất ra **10 cách tính khác nhau** cho kết quả gần với mục tiêu nhất.
""")

with st.sidebar:
    st.header("Nhập liệu")
    nums_in = st.text_input("Các số", "3 5 2 8 1")
    ops_in = st.text_input("Các phép tính", "( ) + / *")
    st.caption("💡 Mẹo: Dùng `/` hoặc `v` để có nhiều kết quả thập phân đa dạng.")
    
    st.divider()
    tolerance = st.slider("Sai số tối đa (+/-)", 0.0, 10.0, 2.0, 0.1)
    run_btn = st.button("🚀 Tạo Report", type="primary")

if run_btn:
    # Xử lý input
    clean_nums = nums_in.replace(',', ' ').split()
    nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
    clean_ops = ops_in.replace(',', ' ').split()
    ops = [x.strip() for x in clean_ops]
    tokens = nums + ops
    
    st.write(f"🧩 **Các mảnh ghép:** `{tokens}`")

    with st.spinner("Đang phân tích hàng nghìn trường hợp..."):
        all_results = solve_jigsaw(tokens, [1, 20], tolerance)
        
        if not all_results:
            st.error("Không tìm thấy phép tính nào trong khoảng sai số này.")
        else:
            c1, c2 = st.columns(2)
            
            # --- HÀM HIỂN THỊ REPORT TOP 10 ---
            def show_top_10_report(target, container):
                # 1. Lọc theo target
                subset = [r for r in all_results if r['target'] == target]
                
                # 2. Sắp xếp theo độ lệch (gần 0 nhất lên đầu)
                subset.sort(key=lambda x: x['diff'])
                
                # 3. Lọc trùng lặp biểu thức (Giữ lại 10 cái expression khác nhau nhất)
                unique_report = []
                seen_exprs = set()
                
                for item in subset:
                    if item['expr'] not in seen_exprs:
                        unique_report.append(item)
                        seen_exprs.add(item['expr'])
                    if len(unique_report) >= 10: # Chỉ lấy 10
                        break
                
                # 4. Hiển thị
                container.subheader(f"🎯 Mục tiêu: {target}")
                
                if not unique_report:
                    container.warning("Không tìm thấy dữ liệu.")
                    return

                for i, item in enumerate(unique_report):
                    rank = i + 1
                    val = item['val']
                    diff = item['diff']
                    expr = item['expr']
                    
                    # Màu sắc: Top 3 màu xanh đậm, còn lại màu thường
                    if rank <= 3:
                        card_color = "#e8f5e9" # Xanh nhạt
                        border_color = "#2e7d32" # Xanh đậm
                        icon = "🏆"
                    else:
                        card_color = "#f8f9fa" # Xám trắng
                        border_color = "#dee2e6" # Xám
                        icon = f"#{rank}"

                    # Hiển thị từng dòng
                    container.markdown(f"""
                    <div style="
                        background-color: {card_color}; 
                        border-left: 5px solid {border_color};
                        padding: 10px; 
                        margin-bottom: 8px;
                        border-radius: 4px;
                    ">
                        <div style="display: flex; justify_content: space-between; align-items: center;">
                            <span style="font-weight: bold; color: #555; font-size: 0.9em;">{icon}</span>
                            <code style="font-size: 1.1em; color: #000; font-weight: bold;">{expr}</code>
                        </div>
                        <div style="display: flex; justify_content: space-between; align-items: center; margin-top: 5px;">
                            <span style="color: {border_color}; font-weight: bold; font-size: 1.1em;">= {val:.5f}</span>
                            <span style="font-size: 0.8em; color: #666;">(Lệch: {diff:.5f})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with c1:
                show_top_10_report(1, c1)
            
            with c2:
                show_top_10_report(20, c2)
