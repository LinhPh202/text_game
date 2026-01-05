import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Ultimate Math Solver", page_icon="🧮")

# --- 1. CORE: HÀM TÍNH TOÁN ---
def safe_eval(expr):
    """Tính toán an toàn, trả về None nếu lỗi"""
    try:
        if "**" in expr: # Check số mũ
            parts = expr.split("**")
            if float(parts[1].split()[0].replace(')', '')) > 6: return None
            
        val = eval(expr, {"__builtins__": None}, {"sqrt": math.sqrt, "factorial": math.factorial})
        
        if isinstance(val, complex) or math.isinf(val) or math.isnan(val):
            return None
        return val
    except:
        return None

def apply_unary(val, op):
    """Tính toán 1 ngôi"""
    try:
        if op == 'sqrt':
            return math.sqrt(val) if val >= 0 else None
        if op == '!':
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-9:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- 2. CORE: BỘ SINH BIỂU THỨC (GENERATOR) ---
def generate_expressions(nums, ops, allow_brackets):
    """
    Hàm sinh tất cả các biểu thức hợp lệ.
    Dùng 'yield' để tiết kiệm bộ nhớ thay vì lưu list khổng lồ.
    """
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # Validation
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    # Chuẩn bị hoán vị
    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    # Loop: Hoán vị Số
    for num_perm in itertools.permutations(nums):
        # Loop: Hoán vị Unary (Căn, Giai thừa)
        for u_perm in unary_perms:
            terms_vals = []
            terms_strs = []
            valid_term = True
            
            for i, n in enumerate(num_perm):
                u_op = u_perm[i]
                if u_op:
                    val = apply_unary(n, u_op)
                    if val is None: valid_term = False; break
                    terms_vals.append(val)
                    if u_op == 'sqrt': terms_strs.append(f"sqrt({n})")
                    else: terms_strs.append(f"{n}!")
                else:
                    terms_vals.append(n)
                    terms_strs.append(str(n))
            
            if not valid_term: continue

            # Loop: Hoán vị Binary (+, -, *, /)
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i]))
                    op_symbol = b_perm[i]
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((op_symbol, py_op))
                base_components.append((terms_strs[-1], terms_vals[-1]))
                
                # Logic Ngoặc
                bracket_configs = [None]
                if allow_brackets:
                    n_terms = len(terms_vals)
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            if i == 0 and j == n_terms - 1: continue
                            bracket_configs.append((i, j))

                # Tính toán cuối cùng
                for cfg in bracket_configs:
                    py_parts = []
                    disp_parts = []
                    term_idx = 0
                    for k, comp in enumerate(base_components):
                        if k % 2 == 0:
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
                        else:
                            op_sym, op_py = comp
                            py_parts.append(op_py)
                            disp_parts.append(op_sym)
                    
                    full_py = "".join(py_parts)
                    full_disp = "".join(disp_parts)
                    final_val = safe_eval(full_py)
                    
                    if final_val is not None:
                        yield final_val, full_disp

# --- 3. CÁC HÀM GIẢI ---

def solve_target_search(nums, ops, allow_brackets, targets, max_tolerance):
    """Chế độ 1: Tìm theo Target"""
    results = []
    seen_exprs = set()
    gen = generate_expressions(nums, ops, allow_brackets)
    if gen == "ERROR_COUNT": return "ERROR_COUNT"
    
    for val, expr in gen:
        for t in targets:
            diff = abs(val - t)
            if diff <= max_tolerance:
                unique_key = f"{expr}_{t}"
                if unique_key not in seen_exprs:
                    results.append({
                        'val': val, 'expr': expr, 'diff': diff,
                        'target_matched': t, 'is_exact': diff < 1e-9
                    })
                    seen_exprs.add(unique_key)
    return results

def solve_optimization(nums, ops, allow_brackets, mode):
    """
    Chế độ 2, 3, 4: Tìm Min/Max theo điều kiện
    mode: 'global_min', 'min_positive', 'max_negative'
    """
    # Khởi tạo giá trị kỷ lục (Record)
    if mode == 'max_negative':
        best_val = float('-inf') # Tìm max nên khởi đầu bằng âm vô cùng
    else:
        best_val = float('inf') # Tìm min nên khởi đầu bằng dương vô cùng

    best_results = []
    seen_exprs = set()
    
    gen = generate_expressions(nums, ops, allow_brackets)
    if gen == "ERROR_COUNT": return "ERROR_COUNT"
    
    for val, expr in gen:
        # Chỉ xét số NGUYÊN
        if abs(val - round(val)) < 1e-9:
            int_val = int(round(val))
            
            # --- BỘ LỌC ĐIỀU KIỆN ---
            if mode == 'min_positive' and int_val <= 0: continue
            if mode == 'max_negative' and int_val >= 0: continue
            
            # --- SO SÁNH KỶ LỤC ---
            update_record = False
            
            if mode == 'max_negative':
                # Tìm âm lớn nhất (gần 0 nhất): Ví dụ -1 lớn hơn -100
                if int_val > best_val: update_record = True
            else:
                # Tìm min (Global hoặc Positive): Ví dụ 1 nhỏ hơn 10
                if int_val < best_val: update_record = True
            
            # Cập nhật danh sách kết quả
            if update_record:
                best_val = int_val
                best_results = [{'val': int_val, 'expr': expr}]
                seen_exprs = {expr}
            elif int_val == best_val:
                if expr not in seen_exprs:
                    best_results.append({'val': int_val, 'expr': expr})
                    seen_exprs.add(expr)
                    
    return best_results, best_val

# --- 4. GIAO DIỆN UI ---
st.title("🧮 Solver: Phương trình Quần Què - Chơi xong Xóa")

# Menu chọn chế độ thông minh
mode_label = st.radio(
    "👉 Chọn mục tiêu bài toán:",
    [
        "🎯 Tìm theo Đích (Target)", 
        "📉 Tìm số nguyên Bé nhất (Global Min)",
        "➕ Tìm số nguyên DƯƠNG bé nhất (Min Positive)",
        "➖ Tìm số nguyên ÂM lớn nhất (Max Negative)"
    ]
)

# Map label sang key code
mode_map = {
    "🎯 Tìm theo Đích (Target)": "target",
    "📉 Tìm số nguyên Bé nhất (Global Min)": "global_min",
    "➕ Tìm số nguyên DƯƠNG bé nhất (Min Positive)": "min_positive",
    "➖ Tìm số nguyên ÂM lớn nhất (Max Negative)": "max_negative"
}
current_mode = mode_map[mode_label]

st.write("---")

# Input Area
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        input_nums = st.text_input("1. Nhập các số:", "5, 5, 5, 5")
    with col2:
        input_ops = st.text_input("2. Nhập phép tính:", "+, -, *")
        st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")

    col3, col4 = st.columns(2)
    with col3:
        # Chỉ hiện ô Target khi ở chế độ Target
        is_disabled = (current_mode != "target")
        input_targets = st.text_input(
            "3. Nhập Target:", 
            "24", 
            disabled=is_disabled,
            help="Chỉ dùng cho chế độ tìm đích"
        )
    with col4:
        if not is_disabled:
            max_tol = st.slider("4. Phạm vi sai số:", 0.0, 10.0, 2.0, 0.1)
        else:
            st.info("Chế độ Tự động sẽ tìm số nguyên tối ưu.")

allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (1 cặp)", value=False)

# Nút Action
if st.button("🚀 Giải bài toán"):
    try:
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        else:
            # === XỬ LÝ THEO CHẾ ĐỘ ===
            
            # 1. Chế độ TARGET
            if current_mode == "target":
                target_list = [float(x.strip()) for x in input_targets.split(',') if x.strip() != '']
                target_list.sort()
                
                if not target_list:
                    st.error("Vui lòng nhập Target.")
                else:
                    with st.spinner('Đang tìm kiếm...'):
                        res = solve_target_search(nums, ops, allow_brackets=allow_bracket, targets=target_list, max_tolerance=max_tol)
                        
                        if res == "ERROR_COUNT":
                            st.error("❌ Lỗi: Số lượng phép tính không khớp.")
                        else:
                            # Hiển thị kết quả Target (như cũ)
                            r_map = {t: [] for t in target_list}
                            for r in res: r_map[r['target_matched']].append(r)
                            
                            tabs = st.tabs([f"{'✅' if any(i['is_exact'] for i in r_map[t]) else ('⚠️' if r_map[t] else '❌')} {t}" for t in target_list])
                            
                            for i, t in enumerate(target_list):
                                with tabs[i]:
                                    dat = r_map[t]
                                    if not dat: st.error(f"Không tìm thấy {t}")
                                    else:
                                        dat.sort(key=lambda x: x['diff'])
                                        exacts = [x for x in dat if x['is_exact']]
                                        approxs = [x for x in dat if not x['is_exact']]
                                        
                                        if exacts:
                                            st.success(f"🎉 CHÍNH XÁC")
                                            for e in exacts[:10]: st.code(f"{e['expr']} = {t}")
                                        
                                        if approxs:
                                            if exacts: 
                                                with st.expander("Kết quả gần đúng"):
                                                    for a in approxs[:5]: st.code(f"{a['expr']} = {a['val']:.5f}")
                                            else:
                                                st.warning("⚠️ GẦN ĐÚNG")
                                                for a in approxs[:5]: 
                                                    st.write(f"Sai số: {a['diff']:.5f}")
                                                    st.code(f"{a['expr']} = {a['val']:.5f}")

            # 2. Chế độ TỐI ƯU (Global Min, Min Pos, Max Neg)
            else:
                msg_map = {
                    "global_min": "Đang tìm số nguyên BÉ NHẤT toàn cục...",
                    "min_positive": "Đang tìm số nguyên DƯƠNG (>0) bé nhất...",
                    "max_negative": "Đang tìm số nguyên ÂM (<0) lớn nhất..."
                }
                
                with st.spinner(msg_map[current_mode]):
                    results, best_val = solve_optimization(nums, ops, allow_bracket, current_mode)
                    
                    if results == "ERROR_COUNT":
                        st.error("❌ Lỗi: Số lượng phép tính không khớp.")
                    elif not results:
                        st.warning("Không tìm thấy số nguyên nào thỏa mãn điều kiện này.")
                    else:
                        # Tiêu đề kết quả
                        title_map = {
                            "global_min": f"🏆 SỐ NGUYÊN BÉ NHẤT: {best_val}",
                            "min_positive": f"🏆 SỐ NGUYÊN DƯƠNG BÉ NHẤT: {best_val}",
                            "max_negative": f"🏆 SỐ NGUYÊN ÂM LỚN NHẤT (Gần 0 nhất): {best_val}"
                        }
                        st.success(title_map[current_mode])
                        
                        st.write(f"Tìm thấy **{len(results)}** cách tính:")
                        for r in results[:10]:
                            st.code(f"{r['expr']} = {r['val']}")

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
