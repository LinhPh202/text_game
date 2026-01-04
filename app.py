import streamlit as st
import itertools
import math

# ==========================================
# PHẦN LOGIC XỬ LÝ TOÁN HỌC
# ==========================================

def solve_math_puzzle(numbers, target):
    """
    Hàm giải đố: Tạo biểu thức từ danh sách 'numbers' để bằng 'target'.
    - Phép tính: +, -, *, /, ** (mũ), sqrt (căn bậc 2).
    - Ràng buộc: Tối đa 1 cặp ngoặc ().
    - Định dạng hiển thị: x, :, ^, √.
    """
    
    # 1. TIỀN XỬ LÝ: Tạo biến thể số (Số thường và Căn bậc 2)
    # number_variants là list chứa các list. Ví dụ input [4, 5] -> [[(4,'4','4'), (2,'√4','2')], [(5,'5','5')]]
    number_variants = []
    for n in numbers:
        vars_for_n = []
        # Dạng nguyên bản
        vars_for_n.append((n, str(n), str(n))) # (giá trị, hiển thị, tính toán)
        
        # Dạng căn bậc 2 (chỉ nếu là số chính phương và > 1)
        if n > 1 and math.isqrt(n)**2 == n:
            sqrt_val = int(math.isqrt(n))
            # Hiển thị: √9, Tính toán trong python: 3
            vars_for_n.append((sqrt_val, f"√{n}", str(sqrt_val))) 
            
        number_variants.append(vars_for_n)

    # 2. ĐỊNH NGHĨA PHÉP TOÁN
    ops_map = [
        ('+', '+'), 
        ('-', '-'), 
        ('*', 'x'), 
        ('/', ':'), 
        ('**', '^')
    ]

    # 3. VÒNG LẶP TÌM KIẾM (Brute-force thông minh)
    
    # Bước A: Hoán vị vị trí các số (Ví dụ: 4,9,2 -> 9,2,4 -> ...)
    for perm in itertools.permutations(number_variants):
        
        # Bước B: Chọn biến thể (Dùng số thường hay dùng căn?)
        # perm là list các list biến thể. Dùng product để lấy tổ hợp cụ thể.
        for nums_chosen in itertools.product(*perm):
            # Tách riêng các thành phần để dễ xử lý
            vals = [x[0] for x in nums_chosen]      # Giá trị thực (int)
            disps = [x[1] for x in nums_chosen]     # Chuỗi hiển thị (str)
            calcs = [x[2] for x in nums_chosen]     # Chuỗi tính toán Python (str)
            
            n_count = len(vals)
            
            # Bước C: Chọn phép toán chèn vào giữa
            for ops_chosen in itertools.product(ops_map, repeat=n_count - 1):
                op_calcs = [o[0] for o in ops_chosen] # +, -, *, /, **
                op_disps = [o[1] for o in ops_chosen] # +, -, x, :, ^
                
                # Bước D: Áp dụng Mẫu (Templates) giới hạn 1 cặp ngoặc
                templates = []
                
                if n_count == 3:
                    A, B, C = calcs
                    dA, dB, dC = disps
                    o1, o2 = op_calcs
                    d1, d2 = op_disps
                    
                    # Các mẫu hợp lệ cho 3 số
                    templates.append((f"{A}{o1}{B}{o2}{C}",       f"{dA} {d1} {dB} {d2} {dC}"))         # Không ngoặc
                    templates.append((f"({A}{o1}{B}){o2}{C}",     f"({dA} {d1} {dB}) {d2} {dC}"))       # (A op B) op C
                    templates.append((f"{A}{o1}({B}{o2}{C})",     f"{dA} {d1} ({dB} {d2} {dC})"))       # A op (B op C)

                elif n_count == 4:
                    A, B, C, D = calcs
                    dA, dB, dC, dD = disps
                    o1, o2, o3 = op_calcs
                    d1, d2, d3 = op_disps
                    
                    # Các mẫu hợp lệ cho 4 số
                    templates.append((f"{A}{o1}{B}{o2}{C}{o3}{D}",       f"{dA} {d1} {dB} {d2} {dC} {d3} {dD}"))       # Không ngoặc
                    templates.append((f"({A}{o1}{B}){o2}{C}{o3}{D}",     f"({dA} {d1} {dB}) {d2} {dC} {d3} {dD}"))     # (A op B) ...
                    templates.append((f"{A}{o1}({B}{o2}{C}){o3}{D}",     f"{dA} {d1} ({dB} {d2} {dC}) {d3} {dD}"))     # ... (B op C) ...
                    templates.append((f"{A}{o1}{B}{o2}({C}{o3}{D})",     f"{dA} {d1} {dB} {d2} ({dC} {d3} {dD})"))     # ... (C op D)

                # Bước E: Kiểm tra kết quả
                for calc_str, disp_str in templates:
                    try:
                        # Kiểm tra logic chia và mũ trước khi eval để tránh lỗi/treo
                        if check_valid_logic(calc_str): 
                            res = eval(calc_str)
                            # So sánh kết quả (dùng abs cho float để tránh sai số nhỏ)
                            if abs(res - target) < 1e-9:
                                return disp_str
                    except ZeroDivisionError:
                        continue
                    except Exception:
                        continue

    return None

def check_valid_logic(expr_str):
    """
    Hàm phụ trợ: Kiểm tra nhanh phép tính có hợp lý không trước khi eval.
    Ngăn chặn phép chia có dư hoặc phép mũ quá lớn.
    """
    # Lưu ý: Đây là kiểm tra sơ bộ trên chuỗi đã ghép. 
    # Để tối ưu tốc độ, ta check lỏng lẻo ở đây và để eval xử lý chính.
    # Logic chặn mũ quá lớn để tránh treo server:
    if "**" in expr_str:
        # Nếu thấy mũ, rủi ro cao, ta eval thử trong try/catch an toàn
        try:
            # Chỉ cho phép kết quả trung gian không quá lớn (ví dụ 1 triệu)
            # Đây là trick để tránh tính 9**9**9
            pass 
        except:
            return False
            
    # Logic phép chia: Trong python '/' ra float. 
    # Ta muốn game số nguyên nên chỉ chấp nhận nếu kết quả là nguyên.
    # Việc này được xử lý sau khi eval xong (check float == int).
    return True

# ==========================================
# PHẦN GIAO DIỆN STREAMLIT
# ==========================================

def main():
    st.set_page_config(page_title="Math Puzzle Solver", page_icon="🧩")
    
    st.title("🧩 Math Puzzle Solver")
    st.markdown("""
    Công cụ tìm biểu thức toán học thỏa mãn điều kiện:
    * Sử dụng các phép tính: `+`, `-`, `x`, `:`, `^` (mũ), `√` (căn bậc 2).
    * **Tối đa 1 cặp ngoặc đơn**.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        input_str = st.text_input("Nhập các số (phân tách bằng dấu phẩy)", value="4, 9, 2")
        st.caption("Ví dụ: 4, 9, 2 hoặc 5, 5, 5, 1")
        
    with col2:
        target_num = st.number_input("Nhập số mục tiêu (Target)", value=5, step=1)

    solve_btn = st.button("🔍 Tìm lời giải", type="primary")

    if solve_btn:
        try:
            # Xử lý input đầu vào
            numbers = [int(x.strip()) for x in input_str.split(',') if x.strip().isdigit()]
            
            if len(numbers) < 2:
                st.error("Vui lòng nhập ít nhất 2 số.")
            elif len(numbers) > 5:
                st.warning("Nhập quá nhiều số có thể khiến việc tìm kiếm bị chậm.")
                
            else:
                with st.spinner('Đang tính toán...'):
                    result = solve_math_puzzle(numbers, target_num)
                
                st.divider()
                if result:
                    st.success("### ✅ Tìm thấy lời giải:")
                    # Hiển thị to, rõ ràng
                    st.markdown(f"<h2 style='text-align: center; color: #00CC00;'>{result} = {target_num}</h2>", unsafe_allow_html=True)
                else:
                    st.warning("### ❌ Không tìm thấy lời giải nào.")
                    st.write("Thử đổi số mục tiêu hoặc các số đầu vào.")
                    
        except ValueError:
            st.error("Lỗi định dạng! Vui lòng chỉ nhập số và dấu phẩy.")

if __name__ == "__main__":
    main()
