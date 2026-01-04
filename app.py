import streamlit as st
import itertools
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver: Tùy Chọn Ngoặc", page_icon="🎛️", layout="wide")

# --- DANH SÁCH MẪU CÂU (TEMPLATES) ---
# Mẫu số 0: Không ngoặc (Tính theo PEMDAS chuẩn: Nhân chia trước, cộng trừ sau)
TEMPLATE_NO_BRACKET = ["{0}{5}{1}{6}{2}{7}{3}{8}{4}"]

# Các mẫu có ngoặc (Catalan patterns cho 5 số)
TEMPLATES_WITH_BRACKET = [
    "({0}{5}{1}){6}{2}{7}{3}{8}{4}",           # (A+B)+C+D+E
    "{0}{5}({1}{6}{2}){7}{3}{8}{4}",           # A+(B+C)+D+E
    "{0}{5}{1}{6}({2}{7}{3}){8}{4}",           # A+B+(C+D)+E
    "{0}{5}{1}{6}{2}{7}({3}{8}{4})",           # A+B+C+(D+E)
    "({0}{5}{1}{6}{2}){7}{3}{8}{4}",           # (A+B+C)+D+E
    "{0}{5}({1}{6}{2}{7}{3}){8}{4}",           # A+(B+C+D)+E
    "{0}{5}{1}{6}({2}{7}{3}{8}{4})",           # A+B+(C+D+E)
    "(({0}{5}{1}){6}{2}){7}{3}{8}{4}",         # ((A+B)+C)+D+E
    "({0}{5}({1}{6}{2})){7}{3}{8}{4}",         # (A+(B+C))+D+E
    "{0}{5}(({1}{6}{2}){7}{3}){8}{4}",         # A+((B+C)+D)+E
    "{0}{5}({1}{6}({2}{7}{3})){8}{4}",         # A+(B+(C+D))+E
    "({0}{5}{1}){6}({2}{7}{3}){8}{4}",         # (A+B)+(C+D)+E
    "(({0}{5}{1}){6}{2}{7}{3}){8}{4}",         # ((A+B)+C+D)+E
    "({0}{5}{1}){6}{2}{7}({3}{8}{4})",         # (A+B)+C+(D+E)
    "(({0}{5}{1}){6}({2}{7}{3})){8}{4}",       # ((A+B)+(C+D))+E
    "{0}{5}(({1}{6}{2}){7}({3}{8}{4}))",       # A+((B+C)+(D+E))
]

def solve_math(numbers, operators, targets, tolerance, use_brackets):
    solutions = []
    seen_expr = set()

    # 1. Lọc phép tính nối (Binary Ops)
    # Ta cần đúng 4 phép tính để nối 5 số
    binary_ops_pool = [op for op in operators if op in ['+', '-', '*', '/', '^']]
    
    if len(binary_ops_pool) < 4:
        return [], f"Thiếu phép tính! Bạn nhập {len(binary_ops_pool)} phép nối, nhưng cần tối thiểu 4 phép (+ - * / ^) cho 5 số."

    # 2. Xác định danh sách mẫu sẽ dùng
    # Luôn luôn dùng mẫu không ngoặc
    active_patterns = TEMPLATE_NO_BRACKET[:]
    
    # Nếu user tick chọn dùng ngoặc thì thêm vào
    if use_brackets:
        active_patterns += TEMPLATES_WITH_BRACKET

    # 3. Tạo hoán vị
    # Hoán vị số
    num_perms = list(itertools.permutations(numbers))
    
    # Hoán vị phép tính (Chọn 4 trong số các phép tính đã nhập)
    # set() để loại bỏ các trường hợp trùng lặp nếu user nhập nhiều dấu giống nhau
    op_perms = list(set(itertools.permutations(binary_ops_pool, 4)))

    # 4. Vòng lặp chính
    for n_p in num_perms:
        for o_p in op_perms:
            
            # Chuẩn bị dữ liệu điền vào mẫu
            # Python dùng ** cho mũ, nhưng hiển thị dùng ^
            py_ops = [o.replace('^', '**') for o in o_p]
            display_ops = o_p
            
            # List dữ liệu gộp: 5 Số + 4 Phép tính
            fill_data_py = list(n_p) + list(py_ops)
            fill_data_disp = list(n_p) + list(display_ops)

            for pattern in active_patterns:
                try:
                    # Tạo biểu thức hiển thị
                    expr_disp = pattern.format(*fill_data_disp)

                    if expr_disp in seen_expr: continue
                    seen_expr.add(expr_disp)

                    # Tạo biểu thức tính toán
                    expr_py = pattern.format(*fill_data_py)
                    
                    # TÍNH TOÁN
                    val = eval(expr_py)
                    
                    if isinstance(val, complex): continue
                    
                    # Kiểm tra mục tiêu
                    for t in targets:
                        diff = abs(val - t)
                        if diff <= tolerance:
                            solutions.append({
                                'val': val,
                                'expr': expr_disp,
                                'diff': diff,
                                'target': t
                            })

                except (ValueError, ZeroDivisionError, OverflowError):
                    continue
                    
    return solutions, None

# --- GIAO DIỆN NGƯỜI DÙNG ---
st.title("🎛️ Math Solver: Tùy Chọn")
st.markdown("Nhập 5 số và các phép tính. Hệ thống sẽ tự động hoán vị để tìm kết quả.")

with st.sidebar:
    st.header("1. Nhập liệu")
    nums_in = st.text_input("5 Số (cách nhau bởi dấu cách)", "3 5 2 8 1")
    ops_in = st.text_input("Phép tính (nhập dư cũng được)", "+ - * / ^")
    
    st.divider()
    
    st.header("2. Tùy chọn")
    # --- CHECKBOX QUAN TRỌNG ---
    use_brackets = st.checkbox("Sử dụng Ngoặc ( )", value=False, help="Nếu tích, máy sẽ thử chèn các cặp ngoặc lồng nhau để thay đổi thứ tự tính toán.")
    
    tolerance = st.slider("Sai số cho phép (+/-)", 0.0, 5.0, 0.5, 0.1)
    
    st.divider()
    run_btn = st.button("🚀 Tính Toán", type="primary")

if run_btn:
    try:
        # Xử lý Input
        clean_nums = nums_in.replace(',', ' ').split()
        nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
        
        clean_ops = ops_in.replace(',', ' ').split()
        ops = [x.strip() for x in clean_ops]
        
        if len(nums) != 5:
            st.error(f"Vui lòng nhập đúng 5 con số (Bạn đang nhập {len(nums)} số).")
        else:
            # Thông báo trạng thái
            mode_text = "Có sử dụng ngoặc ( )" if use_brackets else "Không sử dụng ngoặc"
            st.info(f"Đang tính toán... | Chế độ: **{mode_text}**")
            
            with st.spinner("Đang chạy hàng nghìn phép thử..."):
                results, error = solve_math(nums, ops, [1, 20], tolerance, use_brackets)
            
            if error:
                st.error(error)
            elif not results:
                st.warning("Không tìm thấy kết quả nào trong khoảng sai số này.")
            else:
                c1, c2 = st.columns(2)
                
                # Hàm hiển thị Report Top 10
                def show_report(target, container):
                    subset = [r for r in results if r['target'] == target]
                    subset.sort(key=lambda x: x['diff'])
                    
                    # Lọc trùng lặp
                    unique_res = []
                    seen = set()
                    for item in subset:
                        if item['expr'] not in seen:
                            unique_res.append(item)
                            seen.add(item['expr'])
                        if len(unique_res) >= 10: break
                    
                    container.subheader(f"🎯 Mục tiêu: {target}")
                    
                    if not unique_res:
                        container.caption("Không có phương án phù hợp.")
                        return

                    for i, item in enumerate(unique_res):
                        # Logic màu sắc
                        if item['diff'] < 1e-9: # Chính xác
                            border = "2px solid #28a745"
                            bg = "#e8f5e9"
                            icon = "✅"
                        else: # Gần đúng
                            border = "1px solid #ffc107"
                            bg = "#fffcf5"
                            icon = "≈"
                            
                        container.markdown(f"""
                        <div style="border: {border}; background: {bg}; padding: 8px; border-radius: 6px; margin-bottom: 8px;">
                            <div style="font-weight: bold; font-size: 1.1em; color: #333;">{item['expr']}</div>
                            <div style="display: flex; justify_content: space-between; margin-top: 4px;">
                                <span style="color: #155724; font-weight: bold;">{icon} {item['val']:.5f}</span>
                                <span style="color: #666; font-size: 0.85em;">Lệch: {item['diff']:.5f}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with c1: show_report(1, c1)
                with c2: show_report(20, c2)

    except Exception as e:
        st.error(f"Lỗi hệ thống: {e}")
