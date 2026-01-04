import streamlit as st
import itertools
import math
import pandas as pd

# ==========================================
# 1. LOGIC XỬ LÝ TOÁN HỌC
# ==========================================

def get_number_variants(numbers):
    """
    Tạo biến thể cho từng số (Số thường và Căn bậc 2 nếu là số chính phương).
    Input: [4, 5]
    Output: [[(4, '4', '4'), (2, '√4', '2')], [(5, '5', '5')]]
    """
    variants = []
    for n in numbers:
        vars_for_n = []
        # Dạng nguyên bản
        vars_for_n.append((n, str(n), str(n))) 
        
        # Dạng căn bậc 2 (nếu là số chính phương > 1)
        if n > 0 and math.isqrt(n)**2 == n:
            sqrt_val = int(math.isqrt(n))
            vars_for_n.append((sqrt_val, f"√{n}", str(sqrt_val))) 
        
        variants.append(vars_for_n)
    return variants

def check_safe_eval(expr_str):
    """Kiểm tra an toàn trước khi eval (tránh số mũ quá lớn gây treo máy)"""
    if "**" in expr_str:
        # Nếu chuỗi quá dài hoặc có cấu trúc mũ chồng mũ nguy hiểm
        if len(expr_str) > 60: return False
    return True

def generate_expressions(numbers, allowed_ops, use_brackets):
    """
    Sinh ra tất cả các kết quả có thể từ 5 số và các phép tính.
    Trả về danh sách: [{'val': float, 'expr': str}, ...]
    """
    results = []
    seen_formulas = set() # Để loại bỏ trùng lặp công thức

    # 1. Tạo biến thể số (xử lý căn bậc 2)
    number_variants = get_number_variants(numbers)
    
    # Mapping hiển thị phép tính
    ops_display = {'+': '+', '-': '-', '*': 'x', '/': ':', '**': '^'}

    # 2. Vòng lặp Hoán vị vị trí các số
    # Với 5 số, permutations = 120 trường hợp.
    for perm in itertools.permutations(number_variants):
        
        # 3. Chọn biến thể (Dùng số thường hay dùng căn)
        for nums_chosen in itertools.product(*perm):
            vals = [x[0] for x in nums_chosen]      # Giá trị int
            disps = [x[1] for x in nums_chosen]     # Hiển thị
            calcs = [x[2] for x in nums_chosen]     # Python string
            
            n = len(vals) # Thường là 5
            
            # 4. Chọn phép toán (cần n-1 phép toán cho n số)
            # Nếu 5 số cần 4 phép toán.
            # Lưu ý: Nếu allowed_ops quá nhiều, vòng lặp này sẽ rất lớn.
            # product của 5 phép toán cho 4 chỗ trống = 625 loops.
            for ops in itertools.product(allowed_ops, repeat=n-1):
                
                # Tạo danh sách các Template (Mẫu câu)
                templates = []
                
                # Logic tạo chuỗi (A, B, C, D, E và op1, op2, op3, op4)
                # Code này viết tổng quát cho 5 số
                if n == 5:
                    A, B, C, D, E = calcs
                    dA, dB, dC, dD, dE = disps
                    o1, o2, o3, o4 = ops
                    d1, d2, d3, d4 = [ops_display[o] for o in ops]
                    
                    # Mẫu 1: Không ngoặc (Luôn chạy)
                    # Python tự động tính theo PEMDAS
                    templates.append((
                        f"{A}{o1}{B}{o2}{C}{o3}{D}{o4}{E}", 
                        f"{dA} {d1} {dB} {d2} {dC} {d3} {dD} {d4} {dE}"
                    ))
                    
                    # Mẫu 2: Dùng ngoặc (Nếu user chọn)
                    # Chỉ thêm 1 cặp ngoặc đơn giản để code chạy nhanh
                    if use_brackets:
                        # (A o B) ...
                        templates.append((
                            f"({A}{o1}{B}){o2}{C}{o3}{D}{o4}{E}", 
                            f"({dA} {d1} {dB}) {d2} {dC} {d3} {dD} {d4} {dE}"
                        ))
                        # ... (B o C) ...
                        templates.append((
                            f"{A}{o1}({B}{o2}{C}){o3}{D}{o4}{E}", 
                            f"{dA} {d1} ({dB} {d2} {dC}) {d3} {dD} {d4} {dE}"
                        ))
                        # ... (C o D) ...
                        templates.append((
                            f"{A}{o1}{B}{o2}({C}{o3}{D}){o4}{E}", 
                            f"{dA} {d1} {dB} {d2} ({dC} {d3} {dD}) {d4} {dE}"
                        ))
                        # ... (D o E)
                        templates.append((
                            f"{A}{o1}{B}{o2}{C}{o3}({D}{o4}{E})", 
                            f"{dA} {d1} {dB} {d2} {dC} {d3} ({dD} {d4} {dE})"
                        ))

                # 5. Tính toán và lưu kết quả
                for calc_str, disp_str in templates:
                    if disp_str in seen_formulas: continue
                    
                    try:
                        if check_safe_eval(calc_str):
                            res = eval(calc_str)
                            # Chỉ lưu kết quả hợp lý (không quá lớn, không số phức)
                            if isinstance(res, (int, float)) and abs(res) < 1000000:
                                results.append({'val': res, 'expr': disp_str})
                                seen_formulas.add(disp_str)
                    except (ZeroDivisionError, OverflowError, ValueError):
                        continue
                    except:
                        continue
                        
    return results

# ==========================================
# 2. GIAO DIỆN STREAMLIT
# ==========================================

def main():
    st.set_page_config(page_title="Math Solver Pro", page_icon="🧮", layout="wide")
    
    st.title("🧮 Math Solver: Tìm kết quả gần 1 và 20")
    st.markdown("Nhập 5 số và chọn các phép tính. Hệ thống sẽ sử dụng quy tắc **PEDAMS** (Nhân chia trước, cộng trừ sau).")

    # --- INPUT AREA ---
    with st.container():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            input_str = st.text_input("Nhập 5 số (cách nhau dấu phẩy)", value="5, 5, 5, 5, 5")
            st.caption("Ví dụ: 1, 2, 3, 4, 5")
            
        with col2:
            # Multi-select cho phép tính
            ops_selected = st.multiselect(
                "Chọn các phép tính được dùng:",
                ['+', '-', '*', '/', '**'],
                default=['+', '-', '*', '/'],
                format_func=lambda x: {'+':'Cộng (+)', '-':'Trừ (-)', '*':'Nhân (x)', '/':'Chia (:)', '**':'Mũ (^)'}[x]
            )
            
        with col3:
            st.write("Tùy chọn ngoặc:")
            use_brackets = st.checkbox("Dùng ngoặc ()", value=False)
            st.caption("Chỉ thêm tối đa 1 cặp ngoặc.")

    run_btn = st.button("🚀 Bắt đầu tính toán", type="primary", use_container_width=True)

    # --- PROCESS & OUTPUT ---
    if run_btn:
        # Validate Input
        try:
            numbers = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
        except:
            st.error("Lỗi: Vui lòng chỉ nhập số nguyên ngăn cách bởi dấu phẩy.")
            return

        if len(numbers) != 5:
            st.warning(f"⚠️ Bạn đang nhập {len(numbers)} số. Chương trình tối ưu nhất cho **5 số**.")
        
        if not ops_selected:
            st.error("Vui lòng chọn ít nhất 1 phép tính.")
            return

        # Kiểm tra căn bậc 2
        sqrts = [f"√{n}={int(math.isqrt(n))}" for n in numbers if n > 0 and math.isqrt(n)**2 == n]
        if sqrts:
            st.info(f"💡 Đã kích hoạt phép Căn bậc 2 cho: {', '.join(sqrts)}")

        with st.spinner("Đang phân tích hàng ngàn khả năng..."):
            # Chạy thuật toán
            all_results = generate_expressions(numbers, ops_selected, use_brackets)
            
            if not all_results:
                st.error("Không tìm thấy kết quả hợp lệ nào.")
                return

            # --- LỌC KẾT QUẢ ---
            # 1. Tìm Top kết quả gần 1
            df = pd.DataFrame(all_results)
            
            # Tính khoảng cách
            df['diff_1'] = abs(df['val'] - 1)
            df['diff_20'] = abs(df['val'] - 20)

            # Lọc và sort cho Target 1 (Lấy top 10 công thức khác biệt)
            df_near_1 = df.sort_values('diff_1').drop_duplicates(subset=['val', 'expr']).head(15)
            
            # Lọc và sort cho Target 20
            df_near_20 = df.sort_values('diff_20').drop_duplicates(subset=['val', 'expr']).head(15)

        # --- HIỂN THỊ KẾT QUẢ ---
        st.divider()
        out_col1, out_col2 = st.columns(2)

        with out_col1:
            st.subheader("🎯 Kết quả Gần 1 nhất")
            if not df_near_1.empty:
                for index, row in df_near_1.iterrows():
                    val = row['val']
                    # Format số đẹp (nếu là int thì bỏ .0)
                    val_str = f"{int(val)}" if val == int(val) else f"{val:.4f}"
                    
                    # Highlight nếu trúng phóc
                    if row['diff_1'] < 0.000001:
                        st.success(f"**{row['expr']} = {val_str}**")
                    else:
                        st.write(f"{row['expr']} = **{val_str}**")
            else:
                st.write("Không có dữ liệu.")

        with out_col2:
            st.subheader("🎯 Kết quả Gần 20 nhất")
            if not df_near_20.empty:
                for index, row in df_near_20.iterrows():
                    val = row['val']
                    val_str = f"{int(val)}" if val == int(val) else f"{val:.4f}"
                    
                    if row['diff_20'] < 0.000001:
                        st.success(f"**{row['expr']} = {val_str}**")
                    else:
                        st.write(f"{row['expr']} = **{val_str}**")
            else:
                st.write("Không có dữ liệu.")

if __name__ == "__main__":
    main()
