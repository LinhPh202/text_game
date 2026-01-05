import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver: Min & Target", page_icon="🧮")

# --- 1. CÁC HÀM TÍNH TOÁN (CORE) ---
def safe_eval(expr):
    """Tính toán biểu thức chuỗi an toàn"""
    try:
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
    """Tính toán 1 ngôi"""
    try:
        if op == 'sqrt':
            return math.sqrt(val) if val >= 0 else None
        if op == '!':
            if 0 <= val <= 10 and abs(val - round(val)) < 1e-9:
                return math.factorial(int(round(val)))
    except: return None
    return None

# --- 2. THUẬT TOÁN SINH HOÁN VỊ (DÙNG CHUNG) ---
def generate_expressions(nums, ops, allow_brackets):
    """Hàm generator để sinh ra các biểu thức và giá trị, giúp tái sử dụng code"""
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    for num_perm in itertools.permutations(nums):
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

            for b_perm in set(itertools.permutations(binary_ops_pool)):
                base_components = []
                for i in range(len(b_perm)):
                    base_components.append((terms_strs[i], terms_vals[i]))
                    op_symbol = b_perm[i]
                    py_op = "**" if op_symbol == '^' else op_symbol
                    base_components.append((op_symbol, py_op))
                base_components.append((terms_strs[-1], terms_vals[-1]))
                
                bracket_configs = [None]
                if allow_brackets:
                    n_terms = len(terms_vals)
                    for i in range(n_terms - 1):
                        for j in range(i + 1, n_terms):
                            if i == 0 and j == n_terms - 1: continue
                            bracket_configs.append((i, j))

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

# --- 3. CÁC HÀM GIẢI CỤ THỂ ---

def solve_multi_targets(nums, ops, allow_brackets, targets, max_tolerance):
    """Tìm theo Đích"""
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

def solve_find_min(nums, ops, allow_brackets):
    """Tìm số nguyên nhỏ nhất (Min Integer)"""
    min_val = float('inf')
    best_results = []
    seen_exprs = set()
    
    gen = generate_expressions(nums, ops, allow_brackets)
    if gen == "ERROR_COUNT": return "ERROR_COUNT"
    
    for val, expr in gen:
        # 1. Kiểm tra có phải số nguyên không (sai số cực nhỏ)
        if abs(val - round(val)) < 1e-9:
            int_val = int(round(val))
            
            # 2. So sánh Min
            if int_val < min_val:
                # Tìm thấy kỷ lục mới -> Reset list và cập nhật min
                min_val = int_val
                best_results = [{'val': int_val, 'expr': expr}]
                seen_exprs = {expr}
            elif int_val == min_val:
                # Bằng kỷ lục hiện tại -> Thêm vào list (nếu chưa trùng)
                if expr not in seen_exprs:
                    best_results.append({'val': int_val, 'expr': expr})
                    seen_exprs.add(expr)
                    
    return best_results, min_val

# --- 4. GIAO DIỆN STREAMLIT ---
st.title("🧮 Solver: Đa năng")

# Chọn chế độ
mode = st.radio(
    "Chọn chế độ:",
    ["🎯 Tìm theo Đích (Target)", "📉 Tìm Min (Số nguyên bé nhất)"],
    horizontal=True
)

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
        # Logic: Disable ô Target nếu đang ở chế độ Min
        is_target_disabled = (mode == "📉 Tìm Min (Số nguyên bé nhất)")
        input_targets = st.text_input(
            "3. Nhập các Đích (Target):", 
            "24", 
            disabled=is_target_disabled,
            help="Ô này bị khóa khi chọn chế độ Tìm Min"
        )
    with col4:
        if not is_target_disabled:
            max_tol = st.slider("4. Phạm vi sai số (+/-):", 0.0, 10.0, 2.0, 0.1)
        else:
            st.info("Chế độ Min sẽ tự động tìm số nguyên nhỏ nhất.")

allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (Tối đa 1 cặp)", value=False)

if st.button("🚀 Thực hiện"):
    try:
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        else:
            
            # --- CHẾ ĐỘ 1: TÌM MIN ---
            if mode == "📉 Tìm Min (Số nguyên bé nhất)":
                with st.spinner("Đang quét tất cả các khả năng để tìm Min..."):
                    results, min_val = solve_find_min(nums, ops, allow_bracket)
                    
                    if results == "ERROR_COUNT":
                        st.error("❌ Lỗi: Số lượng phép tính không khớp với số lượng con số.")
                    elif not results:
                        st.warning("Không tìm thấy bất kỳ kết quả SỐ NGUYÊN nào từ các phép tính này.")
                    else:
                        st.success(f"🏆 GIÁ TRỊ NHỎ NHẤT TÌM ĐƯỢC LÀ: {min_val}")
                        st.write(f"Tìm thấy **{len(results)}** cách để tạo ra số **{min_val}**:")
                        
                        for r in results[:10]: # Hiện top 10 cách
                            st.code(f"{r['expr']} = {r['val']}")

            # --- CHẾ ĐỘ 2: TÌM TARGET (CŨ) ---
            else:
                target_list = [float(x.strip()) for x in input_targets.split(',') if x.strip() != '']
                target_list.sort()
                
                if len(target_list) == 0:
                    st.error("⚠️ Vui lòng nhập ít nhất 1 Target.")
                else:
                    with st.spinner(f'Đang tính toán...'):
                        all_results = solve_multi_targets(nums, ops, allow_bracket, target_list, max_tol)
                        
                        if all_results == "ERROR_COUNT":
                            st.error("❌ Lỗi: Số lượng phép tính không khớp với số lượng con số.")
                        else:
                            results_map = {t: [] for t in target_list}
                            for r in all_results:
                                results_map[r['target_matched']].append(r)
                            
                            tab_names = []
                            for t in target_list:
                                res = results_map[t]
                                if not res: tab_names.append(f"❌ {t}")
                                elif any(r['is_exact'] for r in res): tab_names.append(f"✅ {t}")
                                else: tab_names.append(f"⚠️ {t}")
                                    
                            tabs = st.tabs(tab_names)
                            
                            for i, t in enumerate(target_list):
                                with tabs[i]:
                                    t_results = results_map[t]
                                    if not t_results:
                                        st.error(f"⛔ Không tìm thấy phương trình cho {t} trong phạm vi sai số +/- {max_tol}.")
                                    else:
                                        t_results.sort(key=lambda x: x['diff'])
                                        exacts = [r for r in t_results if r['is_exact']]
                                        approxs = [r for r in t_results if not r['is_exact']]
                                        
                                        if exacts:
                                            st.success(f"🎉 **CHÍNH XÁC**")
                                            for ex in exacts[:10]: st.code(f"{ex['expr']} = {t}")
                                            if approxs:
                                                with st.expander("Kết quả gần đúng"):
                                                    for n in approxs[:5]: st.code(f"{n['expr']} = {n['val']:.5f}")
                                        elif approxs:
                                            st.warning(f"⚠️ Chỉ có **GẦN ĐÚNG**")
                                            for n in approxs[:5]:
                                                st.write(f"Sai số: {n['diff']:.5f}")
                                                st.code(f"{n['expr']} = {n['val']:.5f}")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
