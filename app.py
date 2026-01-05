import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Solver: Chính xác hoặc Không", page_icon="🎯")

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

# --- 2. THUẬT TOÁN GIẢI (CHỈ TÌM CHÍNH XÁC) ---
def solve_strict_targets(nums, ops, allow_brackets, targets):
    results = [] 
    seen_exprs = set() 
    
    # Phân loại phép tính
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # CHECK SỐ LƯỢNG
    if len(binary_ops_pool) != len(nums) - 1:
        return "ERROR_COUNT"

    # Hoán vị phép Unary
    u_pool_full = unary_ops_pool + [None] * (len(nums) - len(unary_ops_pool))
    unary_perms = set(itertools.permutations(u_pool_full))

    # VÒNG LẶP CHÍNH
    for num_perm in itertools.permutations(nums):
        for u_perm in unary_perms:
            
            # Tính Unary
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

            # Hoán vị Binary
            for b_perm in set(itertools.permutations(binary_ops_pool)):
                
                # Tạo component
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
                        # --- LOGIC STRICT: CHỈ LẤY CHÍNH XÁC ---
                        for t in targets:
                            # So sánh số thực với độ lệch cực nhỏ (coi như bằng 0)
                            if abs(final_val - t) < 1e-9:
                                unique_key = f"{full_disp}_{t}"
                                if unique_key not in seen_exprs:
                                    results.append({
                                        'val': final_val, 
                                        'expr': full_disp, 
                                        'target_matched': t
                                    })
                                    seen_exprs.add(unique_key)
                                
    return results

# --- 3. GIAO DIỆN STREAMLIT ---
st.title("🎯 Solver: Phương trình Quần què")
st.markdown("Chỉ hiển thị kết quả **CHÍNH XÁC**. Nếu không có sẽ báo lỗi.")

# Input
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        input_nums = st.text_input("1. Nhập các số:", "5, 5, 5, 5")
    with col2:
        input_ops = st.text_input("2. Nhập phép tính:", "+, -, *")
        st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")

    input_targets = st.text_input("3. Nhập các Đích (Target):", "1, 20, 24, 100")
    
allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (Tối đa 1 cặp)", value=False)

if st.button("🚀 Quét chính xác"):
    try:
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        target_list = [float(x.strip()) for x in input_targets.split(',') if x.strip() != '']
        target_list.sort() 
        
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        elif len(target_list) == 0:
            st.error("⚠️ Vui lòng nhập ít nhất 1 Target.")
        else:
            with st.spinner(f'Đang tìm kiếm chính xác...'):
                
                # Gọi hàm Strict
                all_results = solve_strict_targets(nums, ops, allow_bracket, target_list)
                
                if all_results == "ERROR_COUNT":
                    st.error(f"❌ Lỗi: Số lượng phép tính 2 ngôi không khớp với số lượng con số.")
                else:
                    # Gom nhóm kết quả
                    results_map = {t: [] for t in target_list}
                    for r in all_results:
                        results_map[r['target_matched']].append(r)
                    
                    # Tạo tên Tab (✅ hoặc ❌)
                    tab_names = []
                    for t in target_list:
                        if results_map[t]: # Có kết quả (list không rỗng)
                            tab_names.append(f"✅ {t}")
                        else:
                            tab_names.append(f"❌ {t}")
                            
                    # Hiển thị Tabs
                    tabs = st.tabs(tab_names)
                    
                    for i, t in enumerate(target_list):
                        with tabs[i]:
                            t_results = results_map[t]
                            
                            if t_results:
                                # TRƯỜNG HỢP CÓ KẾT QUẢ -> XANH LÁ
                                st.success(f"🎉 **Tìm thấy {len(t_results)} đáp án chính xác cho {t}**")
                                for ex in t_results[:10]:
                                    st.code(f"{ex['expr']} = {t}")
                            else:
                                # TRƯỜNG HỢP KHÔNG CÓ -> ĐỎ
                                st.error(f"⛔ Không tìm thấy phép tính nào ra chính xác {t}.")
                                st.write("Không hiển thị kết quả gần đúng theo yêu cầu.")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
