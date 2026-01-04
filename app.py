import streamlit as st
import itertools
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver PEMDAS", page_icon="🧮")

# --- HÀM XỬ LÝ CHUỖI ---
def solve_pemdas(numbers, operators, targets):
    solutions = []
    
    # Phân loại phép tính
    binary_ops_pool = [] # 2 ngôi: +, -, *, /, ^
    unary_ops_pool = []  # 1 ngôi: v, !
    
    for op in operators:
        if op in ['v', '!']:
            unary_ops_pool.append(op)
        else:
            binary_ops_pool.append(op)
            
    # --- KIỂM TRA ĐIỀU KIỆN TOÁN HỌC ---
    # Để nối 5 số thành 1 chuỗi không ngoặc (A + B * C...), ta cần đúng 4 phép nối (binary).
    # Phép tính 1 ngôi (unary) sẽ dính vào số (ví dụ: 3! hoặc v9).
    
    if len(binary_ops_pool) != 4:
        return None, "Lỗi Toán Học: Với 5 con số, bạn cần chính xác 4 phép tính 2 ngôi (+, -, *, /, ^) để kết nối chúng. Số phép tính còn lại phải là 1 ngôi (v, !)."

    # --- BẮT ĐẦU TÌM KIẾM ---
    # 1. Hoán vị các số (Permutations of Numbers)
    num_perms = list(itertools.permutations(numbers))
    
    # 2. Hoán vị các phép tính 2 ngôi (Permutations of Binary Ops)
    bin_op_perms = list(itertools.set_permutations(binary_ops_pool)) if hasattr(itertools, 'set_permutations') else list(itertools.permutations(binary_ops_pool))
    # Lưu ý: itertools không có set_permutations mặc định, dùng set để lọc trùng sau
    bin_op_perms = list(set(bin_op_perms))

    # 3. Xử lý phép tính 1 ngôi (Unary)
    # Vì bài toán yêu cầu dùng hết 5 phép tính, và ta đã dùng 4 binary, 
    # nên ta giả định chỉ còn 1 phép Unary (hoặc code này hỗ trợ tối đa logic cho 1 unary để chèn vào).
    unary_op = unary_ops_pool[0] if unary_ops_pool else None
    
    seen_formulas = set()

    for n_perm in num_perms:
        for b_perm in bin_op_perms:
            # Cấu trúc cơ bản: N0 [op0] N1 [op1] N2 [op2] N3 [op3] N4
            # Bây giờ ta phải chèn phép Unary (nếu có) vào một trong 5 vị trí số
            
            range_positions = range(5) if unary_op else [0]
            
            for u_pos in range_positions:
                # Xây dựng chuỗi biểu thức để Python eval
                # Python eval sẽ tự động lo Nhân chia trước, Cộng trừ sau
                
                # Tạo list các số dưới dạng chuỗi (để chèn Unary vào)
                str_nums = [str(n) for n in n_perm]
                
                # Chèn Unary vào số tại vị trí u_pos
                if unary_op == 'v':
                    str_nums[u_pos] = f"math.sqrt({str_nums[u_pos]})"
                elif unary_op == '!':
                    str_nums[u_pos] = f"math.factorial({str_nums[u_pos]})"
                
                # Ghép chuỗi: Số0 Op0 Số1 Op1 ...
                # Python dùng ** cho lũy thừa
                py_ops = [op.replace('^', '**') for op in b_perm]
                
                expression = f"{str_nums[0]} {py_ops[0]} {str_nums[1]} {py_ops[1]} {str_nums[2]} {py_ops[2]} {str_nums[3]} {py_ops[3]} {str_nums[4]}"
                
                # Hiển thị đẹp (để in ra màn hình)
                display_ops = b_perm
                display_nums = [str(n) for n in n_perm]
                if unary_op == 'v': display_nums[u_pos] = f"√{n_perm[u_pos]}"
                elif unary_op == '!': display_nums[u_pos] = f"{n_perm[u_pos]}!"
                
                pretty_expr = f"{display_nums[0]} {display_ops[0]} {display_nums[1]} {display_ops[1]} {display_nums[2]} {display_ops[2]} {display_nums[3]} {display_ops[3]} {display_nums[4]}"

                if pretty_expr in seen_formulas:
                    continue
                seen_formulas.add(pretty_expr)

                try:
                    # EVALUATE
                    # Cần bắt lỗi: chia 0, căn số âm, số quá lớn
                    val = eval(expression)
                    
                    # Chỉ lấy số thực, không lấy số phức
                    if isinstance(val, complex): continue
                    
                    # Kiểm tra độ gần với các target
                    for t in targets:
                        if math.isclose(val, t, abs_tol=0.1) or abs(val - t) < 1.0: # Lấy biên độ rộng chút để lọc sau
                            solutions.append({'val': val, 'expr': pretty_expr, 'diff': abs(val - t), 'target': t})
                            
                except (ValueError, ZeroDivisionError, OverflowError):
                    continue

    return solutions, None

# --- GIAO DIỆN ---
st.title("🧮 PEMDAS Puzzle Solver")
st.markdown("""
Giải đố 5 số & 5 phép tính theo quy tắc **Nhân chia trước - Cộng trừ sau**.
**Lưu ý quan trọng:** Để kết nối 5 số thành 1 biểu thức hợp lệ, bạn cần cung cấp **4 phép tính 2 ngôi** (`+ - * / ^`) và **1 phép tính 1 ngôi** (`v !`).
""")

col1, col2 = st.columns(2)
with col1:
    nums_in = st.text_input("5 Số (cách nhau bởi phẩy/cách)", "3, 5, 2, 8, 1")
with col2:
    ops_in = st.text_input("5 Phép tính", "+, *, -, ^, v")

if st.button("🚀 Tính Toán", type="primary"):
    try:
        # Parse Input
        nums = [int(x) if float(x).is_integer() else float(x) for x in nums_in.replace(',', ' ').split()]
        ops = [x.strip() for x in ops_in.replace(',', ' ').split()]
        
        if len(nums) != 5 or len(ops) != 5:
            st.error("Vui lòng nhập đúng 5 số và 5 phép tính.")
            st.stop()
            
        # Run Solver
        with st.spinner("Đang hoán vị và tính toán theo quy tắc ưu tiên..."):
            results, error = solve_pemdas(nums, ops, [1, 20])
        
        if error:
            st.warning(error)
        else:
            if not results:
                st.info("Không tìm thấy kết quả nào đủ gần (sai số < 1). Hãy thử đổi số hoặc phép tính.")
            else:
                st.success(f"Đã tìm thấy {len(results)} phương án khả thi!")
                
                c1, c2 = st.columns(2)
                
                # Kết quả gần 1
                with c1:
                    st.subheader("🎯 Mục tiêu: Gần 1")
                    res_1 = [r for r in results if r['target'] == 1]
                    res_1.sort(key=lambda x: x['diff'])
                    for r in res_1[:5]: # Top 5
                        st.code(f"{r['expr']} = {r['val']:.4f}", language='text')

                # Kết quả gần 20
                with c2:
                    st.subheader("🎯 Mục tiêu: Gần 20")
                    res_20 = [r for r in results if r['target'] == 20]
                    res_20.sort(key=lambda x: x['diff'])
                    for r in res_20[:5]: # Top 5
                        st.code(f"{r['expr']} = {r['val']:.4f}", language='text')
                        
    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")
