import streamlit as st
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver: Diagnostic", page_icon="🔧", layout="wide")

# --- HÀM KIỂM TRA LOẠI THẺ ---
def get_token_type(token):
    if isinstance(token, (int, float)): return "NUM"
    if token in ['+', '-', '*', '/', '^']: return "BIN_OP" # Cầu nối
    if token == 'v': return "UNARY_PRE"
    if token == '!': return "UNARY_POST"
    if token == '(': return "OPEN"
    if token == ')': return "CLOSE"
    return "UNKNOWN"

# --- THUẬT TOÁN QUAY LUI ---
def solve_jigsaw(tokens, target_list, tolerance):
    solutions = []
    seen_expr = set()

    def backtrack(current_expr_list, remaining_tokens, balance, last_type):
        # 1. KẾT THÚC CHUỖI
        if not remaining_tokens:
            if balance == 0 and last_type in ["NUM", "CLOSE", "UNARY_POST"]:
                display_str = "".join([str(x) for x in current_expr_list])
                if display_str in seen_expr: return
                seen_expr.add(display_str)

                try:
                    py_str = display_str.replace('^', '**')
                    py_str = py_str.replace('v', 'math.sqrt') 
                    # Xử lý trường hợp người dùng nhập v(...)
                    # Code này giả định cú pháp Python hợp lệ
                    
                    val = eval(py_str)
                    
                    if isinstance(val, complex): return
                    
                    for t in target_list:
                        diff = abs(val - t)
                        if diff <= tolerance:
                            solutions.append({'val': val, 'expr': display_str, 'diff': diff, 'target': t})
                except:
                    return
            return

        # 2. CHỌN THẺ
        unique_tokens = sorted(list(set(remaining_tokens)), key=str)
        
        for token in unique_tokens:
            t_type = get_token_type(token)
            is_valid = False
            
            # RULE: Không cho phép ghép Số cạnh Số (3 5 -> Sai, phải là 35 hoặc 3*5)
            # Ở đây ta mặc định không ghép số, bắt buộc phải có phép tính
            
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
                if t_type == "OPEN": is_valid = True # Bắt v đi với (
                if t_type == "NUM": is_valid = True  # Hoặc v đi với số (v5)
            elif last_type == "UNARY_POST":
                if t_type in ["BIN_OP", "CLOSE"]: is_valid = True

            if t_type == "CLOSE" and balance <= 0: is_valid = False
            
            if is_valid:
                new_tokens = list(remaining_tokens)
                new_tokens.remove(token)
                new_balance = balance + 1 if t_type == "OPEN" else (balance - 1 if t_type == "CLOSE" else balance)
                
                # Heuristic: Cắt nhánh nếu không đủ token để đóng ngoặc
                if len(new_tokens) < new_balance: continue
                
                backtrack(current_expr_list + [token], new_tokens, new_balance, t_type)

    backtrack([], tokens, 0, "START")
    return solutions

# --- GIAO DIỆN ---
st.title("🔧 Math Solver: Chẩn Đoán Lỗi")
st.markdown("Công cụ này sẽ phân tích xem tại sao bạn không tìm ra kết quả.")

with st.sidebar:
    st.header("Nhập liệu")
    nums_in = st.text_input("Các số", "3 5 2 8 1")
    ops_in = st.text_input("Các phép tính", "( ) + * /") 
    # Mặc định để input gây lỗi để test
    
    st.divider()
    tolerance = st.slider("Sai số (+/-)", 0.0, 10.0, 2.0, 0.1)
    run_btn = st.button("🚀 Chạy & Phân Tích", type="primary")

if run_btn:
    clean_nums = nums_in.replace(',', ' ').split()
    nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
    clean_ops = ops_in.replace(',', ' ').split()
    ops = [x.strip() for x in clean_ops]
    tokens = nums + ops
    
    # --- PHÂN TÍCH LOGIC TOÁN HỌC (DIAGNOSTIC) ---
    num_count = len(nums)
    bin_op_count = sum(1 for op in ops if op in ['+', '-', '*', '/', '^'])
    unary_count = sum(1 for op in ops if op in ['v', '!'])
    bracket_count = sum(1 for op in ops if op in ['(', ')'])
    
    required_bridges = num_count - 1
    
    st.subheader("🔍 Phân tích Input của bạn:")
    col1, col2, col3 = st.columns(3)
    col1.metric("Số lượng Số (Hòn đảo)", num_count)
    col2.metric("Phép nối (Cây cầu)", bin_op_count)
    col3.metric("Ngoặc/Khác", bracket_count + unary_count)
    
    # LOGIC CHECK
    if bin_op_count < required_bridges:
        st.error(f"""
        ❌ **LỖI THIẾU PHÉP TÍNH KẾT NỐI!**
        
        Bạn có **{num_count} con số**, để nối tất cả chúng lại thành 1 chuỗi liên tục, bạn cần tối thiểu **{required_bridges} phép tính 2 ngôi** (`+ - * / ^`).
        
        Hiện tại bạn chỉ cung cấp **{bin_op_count} phép tính**.
        (Các dấu `(` `)` `v` `!` không giúp nối 2 số với nhau).
        
        👉 **Giải pháp:** Hãy thêm {required_bridges - bin_op_count} phép tính nữa vào ô nhập liệu (ví dụ thêm dấu `+` hoặc `*`).
        """)
    else:
        st.success("✅ Số lượng phép tính đủ điều kiện toán học. Đang tìm kiếm...")
        
        with st.spinner("Đang xử lý..."):
            all_results = solve_jigsaw(tokens, [1, 20], tolerance)
            
            if not all_results:
                st.warning("Vẫn không tìm thấy kết quả phù hợp. Có thể các số này không thể tạo ra kết quả mong muốn với các phép tính đã cho.")
            else:
                # HIỂN THỊ KẾT QUẢ (TOP 10)
                st.divider()
                def show_report(target, container):
                    subset = [r for r in all_results if r['target'] == target]
                    subset.sort(key=lambda x: x['diff'])
                    
                    unique_report = []
                    seen = set()
                    for item in subset:
                        if item['expr'] not in seen:
                            unique_report.append(item)
                            seen.add(item['expr'])
                        if len(unique_report) >= 5: break
                    
                    container.caption(f"Mục tiêu: {target}")
                    if not unique_report:
                        container.info("Không có dữ liệu.")
                    for item in unique_report:
                        container.success(f"{item['expr']} = {item['val']:.4f}")

                c1, c2 = st.columns(2)
                with c1: show_report(1, c1)
                with c2: show_report(20, c2)
