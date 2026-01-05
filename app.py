import streamlit as st
import math
import itertools

# Cấu hình trang
st.set_page_config(page_title="Multi-Target Solver", page_icon="🎯")

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

# --- 2. THUẬT TOÁN GIẢI ĐA MỤC TIÊU ---
def solve_multi_targets(nums, ops, allow_brackets, targets, max_tolerance):
    results = [] # List chứa dict kết quả
    seen_exprs = set() 
    
    # Phân loại phép tính
    binary_ops_pool = [op for op in ops if op in ['+', '-', '*', '/', '^']]
    unary_ops_pool = [op for op in ops if op in ['sqrt', '!']]
    
    # CHECK SỐ LƯỢNG: N số cần N-1 phép nối
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
                        # --- LOGIC ĐA MỤC TIÊU ---
                        # Kiểm tra kết quả này với TỪNG target trong danh sách
                        for t in targets:
                            diff = abs(final_val - t)
                            
                            if diff <= max_tolerance:
                                # Key để lọc trùng phải bao gồm cả Target (vì 1 biểu thức có thể gần nhiều target)
                                unique_key = f"{full_disp}_{t}"
                                
                                if unique_key not in seen_exprs:
                                    results.append({
                                        'val': final_val, 
                                        'expr': full_disp, 
                                        'diff': diff,
                                        'target_matched': t, # Lưu lại nó khớp với Target nào
                                        'is_exact': diff < 1e-9
                                    })
                                    seen_exprs.add(unique_key)
                                
    return results

# --- 3. GIAO DIỆN STREAMLIT ---
st.title("🎯 Solver: Phương trình Quần Què")
st.markdown("Tìm công thức cho nhiều con số đích cùng lúc.")

# Input
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        input_nums = st.text_input("1. Nhập các số:", "5, 5, 5, 5")
    with col2:
        input_ops = st.text_input("2. Nhập phép tính:", "+, -, *")
        st.caption("Ví dụ: `+, -, *, /, ^, sqrt, !`")

    # Input Multi-Target
    input_targets = st.text_input("3. Nhập các Đích (Target) cần tìm (cách nhau dấu phẩy):", "1, 20, 24, 100")
    
    max_tol = st.slider("Phạm vi tìm sai số (Backup):", 0.0, 10.0, 2.0, 0.1)

allow_bracket = st.checkbox("✅ Cho phép dùng Ngoặc (Tối đa 1 cặp)", value=False)

if st.button("🚀 Quét tất cả Target"):
    try:
        nums = [float(x.strip()) for x in input_nums.split(',') if x.strip() != '']
        ops = [x.strip().lower() for x in input_ops.split(',') if x.strip() != '']
        
        # Parse Targets
        target_list = [float(x.strip()) for x in input_targets.split(',') if x.strip() != '']
        
        if len(nums) > 6:
            st.error("⚠️ Quá nhiều số! Hãy nhập tối đa 5-6 số.")
        elif len(target_list) == 0:
            st.error("⚠️ Vui lòng nhập ít nhất 1 Target.")
        else:
            with st.spinner(f'Đang tính toán cho {len(target_list)} đích đến...'):
                
                # Gọi hàm giải Đa mục tiêu
                all_results = solve_multi_targets(nums, ops, allow_bracket, target_list, max_tol)
                
                if all_results == "ERROR_COUNT":
                    bin_ops = [op for op in ops if op in ['+', '-', '*', '/', '^']]
                    st.error(f"❌ Lỗi: Có {len(nums)} số thì cần đúng {len(nums)-1} phép nối (+, -, *, /, ^).")
                
                elif not all_results:
                    st.warning("Không tìm thấy kết quả nào phù hợp.")
                
                else:
                    # GIAO DIỆN TAB: Tạo Tab cho mỗi Target
                    # Sắp xếp target list để hiển thị tab theo thứ tự tăng dần
                    target_list.sort()
                    
                    # Tạo tên cho các Tab
                    tab_names = [f"Đích {t}" for t in target_list]
                    tabs = st.tabs(tab_names)
                    
                    # Duyệt qua từng tab và lọc dữ liệu tương ứng
                    for i, t in enumerate(target_list):
                        with tabs[i]:
                            # Lọc kết quả thuộc về Target t
                            t_results = [r for r in all_results if r['target_matched'] == t]
                            
                            if not t_results:
                                st.write(f"❌ Không tìm thấy công thức nào gần **{t}** (trong phạm vi +/- {max_tol}).")
                            else:
                                # Sắp xếp theo độ lệch (diff)
                                t_results.sort(key=lambda x: x['diff'])
                                
                                # Tách nhóm chính xác
                                exacts = [r for r in t_results if r['is_exact']]
                                
                                if exacts:
                                    st.success(f"🎉 Có {len(exacts)} công thức **CHÍNH XÁC** bằng {t}!")
                                    for ex in exacts[:10]:
                                        st.code(f"{ex['expr']} = {t}")
                                else:
                                    st.warning(f"⚠️ Không có kết quả chính xác cho {t}.")
                                    st.info("Các kết quả **GẦN ĐÚNG** nhất:")
                                    for near in t_results[:5]: # Top 5 gần nhất
                                        st.write(f"- Sai số: **{near['diff']:.5f}**")
                                        st.code(f"{near['expr']} = {near['val']:.5f}")

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
