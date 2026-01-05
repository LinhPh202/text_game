import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver: Bắn Trúng Đích", page_icon="🎯")

# --- 1. CÁC HÀM TÍNH TOÁN (CORE) ---
def safe_eval(expr):
    """Tính toán biểu thức chuỗi an toàn"""
    try:
        # Check số mũ để tránh treo máy
        if "**" in expr:
            parts = expr.split("**")
            # Nếu số mũ quá lớn (>6) thì bỏ qua
            if float(parts[1].split()[0].replace(')', '')) > 6: return None
            
        # Eval với math library hỗ trợ sẵn
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "factorial": math.factorial})
        
        # Check lỗi toán học (vô cực, số phức)
        if isinstance(val, complex) or math.isinf(val) or math.isnan(val):
            return None
        return val
    except:
        return None

def apply_unary(val, op):
    """Tính toán 1 ngôi (Căn, Giai thừa)"""
    try:
        if op == 'sqrt':
            return math.sqrt(val) if val >= 0 else None
        if op == '!':
            # Chỉ tính giai thừa cho số dương, gần nguyên và <= 10
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-9:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- 2. THUẬT TOÁN GIẢI (LINEAR PERMUTATION) ---
def solve_exact_target(nums, ops, allow_brackets, target):
    results = []
    seen_exprs = set() # Để lọc trùng
    
    # Phân loại phép tính
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # VALIDATION: Kiểm tra đủ phép tính nối
    # N số cần N-1 phép nối
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    # Chuẩn bị hoán vị phép Unary (gán vào các số)
    # Tạo list gồm các Unary Ops và các slot None (không làm gì)
    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    # --- VÒNG LẶP CHÍNH ---
    # 1. Duyệt qua mọi cách sắp xếp các SỐ (Hoán vị số)
    for num_perm in itertools.permutations(nums):
        
        # 2. Duyệt qua mọi cách gán phép UNARY vào số
        for u_perm in unary_perms:
            
            # Tính giá trị từng số hạng sau khi Unary
            terms_vals = []
            terms_strs = []
            valid_term = True
            
            for i, n in enumerate(num_perm):
                u_op = u_perm[i]
                if u_op:
                    val = apply_unary(n, u_op)
                    if val is None: 
                        valid_term = False; break
                    terms_vals.append(val)
                    if u_op == 'sqrt': terms_strs.append(f"sqrt({n})")
                    else: terms_strs.append(f"{n}!")
                else:
                    terms_vals.append(n)
                    terms_strs.append(str(n))
            
            if not valid_term: continue

            # 3. Duyệt qua mọi cách sắp xếp phép BINARY (Hoán vị phép tính)
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                
                # Tạo danh sách các thành phần (Component) theo thứ tự tuyến tính
                # Dạng: [Số1, Dấu1, Số2, Dấu2, Số3...]
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i]))
                    op_symbol = b_perm[i]
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((op_symbol, py_op))
                base_components.append((terms_strs[-1], terms_vals[-1]))
                
                # 4. XỬ LÝ NGOẶC (Brackets)
                bracket_configs = [None] # Mặc định: Không ngoặc
                
                if allow_brackets:
                    n_terms = len(terms_vals)
                    # Thử đặt 1 cặp ngoặc vào các vị trí hợp lệ
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            # Bỏ qua trường hợp bao toàn bộ (vô nghĩa)
                            if i == 0 and j == n_terms - 1: continue
                            bracket_configs.append((i, j))

                # 5. TÍNH TOÁN & KIỂM TRA TARGET
                for cfg in bracket_configs:
                    py_parts = []
                    disp_parts = []
                    
                    term_idx = 0
                    for k, comp in enumerate(base_components):
                        if k % 2 == 0: # Là SỐ
                            t_str, t_val = comp
                            
                            # Mở ngoặc
                            if cfg and term_idx == cfg[0]:
                                py_parts.append("(")
                                disp_parts.append("(")
                            
                            py_parts.append(str(t_val))
                            disp_parts.append(t_str)
                            
                            # Đóng ngoặc
                            if cfg and term_idx == cfg[1]:
                                py_parts.append(")")
                                disp_parts.append(")")
                            
                            term_idx += 1
                        else: # Là PHÉP TÍNH
                            op_sym, op_py = comp
                            py_parts.append(op_py)
                            disp_parts.append(op_sym)
                    
                    full_py = "".join(py_parts)
                    full_disp = "".join(disp_parts)
                    
                    final_val = safe_eval(full_py)
                    
                    if final_val is not None:
                        # KIỂM TRA CHÍNH XÁC (Sai số cực nhỏ < 1e-9)
                        if abs(final_val - target) < 1e-9:
                            if full_disp not in seen_exprs:
                                results.append({'val': final_val, 'expr': full_disp})
                                seen_exprs.add(full_disp)
                                
    return results

# --- 3. GIAO DIỆN STREAMLIT ---
st.title("🎯 Solver: Bắn Trúng Đích")
st.markdown("""
Nhập số, phép tính và **Giá trị mục tiêu**. Máy sẽ tìm cách xếp hình để ra kết quả **chính xác**.
""")

# Khu vực nhập liệu
with st.container():
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        input_nums = st.text_input("1. Nhập các số:", "5, 5, 5, 5")
    with col2:
        input_ops = st.text_input("2. Nhập phép tính:", "+, -, *")
        st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")
    with col3:
        target_val = st.number_input("3. Đích (Target):", value=24.0, step=1.0)

st.write("---")
allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc? (Tối đa 1 cặp)", value=False)
if not allow_bracket:
    st.caption("🔒 Chế độ tính thẳng tuột (Nhân chia trước, cộng trừ sau).")
else:
    st.caption("💡 Máy sẽ thử thêm việc đóng ngoặc cho 1 cụm phép tính.")

# Nút chạy
if st.button("🚀 Tìm công thức"):
    try:
        # Parse dữ liệu
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        # Cảnh báo hiệu năng
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        else:
            with st.spinner(f'Đang tìm cách tạo ra số {target_val}...'):
                # Gọi hàm giải
                res = solve_exact_target(nums, ops, allow_bracket, target_val)
                
                if res == "ERROR_COUNT":
                    bin_ops = [op for op in ops if op in ['+', '-', '*', '/', '^']]
                    st.error(f"""
                    ❌ **Lỗi Logic:**
                    Bạn có **{len(nums)} số** thì cần đúng **{len(nums)-1} phép nối** (+, -, *, /, ^).
                    Bạn đang nhập: {len(bin_ops)}.
                    """)
                elif not res:
                    st.warning(f"Rất tiếc, không tìm thấy phép tính nào ra chính xác {target_val}.")
                else:
                    st.success(f"🎉 Tìm thấy {len(res)} cách tính ra {target_val}!")
                    
                    # Hiển thị kết quả đẹp
                    for i, s in enumerate(res, 1):
                        # Dùng st.empty để tạo khoảng cách nhỏ
                        col_a, col_b = st.columns([1, 4])
                        with col_a:
                            st.write(f"Cách {i}:")
                        with col_b:
                            # Hiển thị dạng code block cho dễ nhìn
                            st.code(f"{s['expr']} = {target_val}")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
