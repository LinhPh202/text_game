import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver: Phương Trình Quần Què", page_icon="🎯")

# --- 1. CÁC HÀM TÍNH TOÁN (CORE) ---
def safe_eval(expr):
    """Tính toán biểu thức chuỗi an toàn"""
    try:
        # Check số mũ quá lớn
        if "**" in expr:
            parts = expr.split("**")
            if float(parts[1].split()[0].replace(')', '')) > 6: return None
            
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "factorial": math.factorial})
        
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
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-9:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- 2. THUẬT TOÁN GIẢI ---
def solve_best_effort(nums, ops, allow_brackets, target, max_tolerance):
    results = []
    seen_exprs = set() 
    
    # Phân loại phép tính
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # CHECK LOGIC SỐ LƯỢNG: N số cần N-1 phép nối
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    # Hoán vị phép Unary
    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    # VÒNG LẶP CHÍNH
    for num_perm in itertools.permutations(nums):
        for u_perm in unary_perms:
            
            # Tính giá trị các số hạng sau khi Unary
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

            # Hoán vị phép tính Binary
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                
                # Tạo component tuyến tính
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i]))
                    op_symbol = b_perm[i]
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((op_symbol, py_op))
                base_components.append((terms_strs[-1], terms_vals[-1]))
                
                # Xử lý Ngoặc
                bracket_configs = [None]
                if allow_brackets:
                    n_terms = len(terms_vals)
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            if i == 0 and j == n_terms - 1: continue
                            bracket_configs.append((i, j))

                # Tính toán
                for cfg in bracket_configs:
                    py_parts = []
                    disp_parts = []
                    
                    term_idx = 0
                    for k, comp in enumerate(base_components):
                        if k % 2 == 0: # Số
                            t_str, t_val = comp
                            if cfg and term_idx == cfg[0]:
                                py_parts.append("(")
                                disp_parts.append("(")
                            py_parts.append(str(t_val))
                            disp_parts.append(t_str)
                            if cfg and term_idx == cfg[1]:
                                py_parts.append(")")
                                disp_parts.append(")")
                            term_idx += 1
                        else: # Dấu
                            op_sym, op_py = comp
                            py_parts.append(op_py)
                            disp_parts.append(op_sym)
                    
                    full_py = "".join(py_parts)
                    full_disp = "".join(disp_parts)
                    
                    final_val = safe_eval(full_py)
                    
                    if final_val is not None:
                        # LOGIC MỚI: Tính độ lệch
                        diff = abs(final_val - target)
                        
                        # Chỉ lưu nếu nằm trong sai số cho phép (để tối ưu bộ nhớ)
                        if diff <= max_tolerance:
                            if full_disp not in seen_exprs:
                                results.append({
                                    'val': final_val, 
                                    'expr': full_disp, 
                                    'diff': diff,
                                    'is_exact': diff < 1e-9 # Đánh dấu chính xác
                                })
                                seen_exprs.add(full_disp)
                                
    return results

# --- 3. GIAO DIỆN STREAMLIT ---
st.title("🎯 Solver: Phương Trình Quần Què")
st.markdown("""
- Máy sẽ tìm kết quả **Chính xác (Target)** trước.
- Nếu không có, máy sẽ tự tìm kết quả **Sai số thấp nhất**.
""")

# Input
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        input_nums = st.text_input("1. Nhập các số:", "5, 5, 5, 5")
    with col2:
        input_ops = st.text_input("2. Nhập phép tính:", "+, -, *")
        st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")

    col3, col4 = st.columns(2)
    with col3:
        target_val = st.number_input("3. Đích (Target):", value=24.0, step=1.0)
    with col4:
        # Cho phép người dùng chỉnh sai số tối đa chấp nhận được để tìm kiếm
        max_tol = st.slider("Phạm vi tìm sai số (Backup):", 0.0, 10.0, 5.0, 0.1)

st.write("---")
allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (Tối đa 1 cặp)", value=False)

if st.button("🚀 Giải bài toán"):
    try:
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        else:
            with st.spinner(f'Đang tìm cách tạo ra {target_val}...'):
                # Tìm tất cả kết quả trong phạm vi sai số
                results = solve_best_effort(nums, ops, allow_bracket, target_val, max_tol)
                
                if results == "ERROR_COUNT":
                    bin_ops = [op for op in ops if op in ['+', '-', '*', '/', '^']]
                    st.error(f"❌ Lỗi: Có {len(nums)} số thì cần đúng {len(nums)-1} phép nối (+, -, *, /, ^). Bạn nhập {len(bin_ops)}.")
                
                elif not results:
                    st.warning(f"Không tìm thấy bất kỳ kết quả nào trong phạm vi sai số +/- {max_tol}.")
                
                else:
                    # Sắp xếp kết quả: Ưu tiên sai số thấp nhất (diff tăng dần)
                    results.sort(key=lambda x: x['diff'])
                    
                    # Tách nhóm Chính xác
                    exact_matches = [r for r in results if r['is_exact']]
                    
                    # LOGIC HIỂN THỊ THÔNG MINH
                    if exact_matches:
                        st.success(f"🎉 Tuyệt vời! Tìm thấy {len(exact_matches)} kết quả CHÍNH XÁC!")
                        for i, s in enumerate(exact_matches[:10], 1): # Chỉ hiện 10 cái đầu
                            st.code(f"{s['expr']} = {target_val}")
                    else:
                        st.warning(f"⚠️ Không có kết quả chính xác tuyệt đối.")
                        st.info(f"👉 Dưới đây là top 5 kết quả GẦN ĐÚNG nhất (Sai số nhỏ nhất):")
                        
                        count = 0
                        for s in results:
                            # Bỏ qua nếu diff quá lớn (giữ lại logic top best)
                            st.write(f"**Sai số: {s['diff']:.5f}**")
                            st.code(f"{s['expr']} = {s['val']:.5f}")
                            count += 1
                            if count >= 5: break # Chỉ lấy top 5 sai số

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
