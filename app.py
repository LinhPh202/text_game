import streamlit as st
import itertools
import math

# --- CẤU HÌNH ---
st.set_page_config(page_title="Math Solver PEMDAS", page_icon="🧮", layout="wide")

# --- HÀM XỬ LÝ TOÁN HỌC ---
def solve_pemdas(numbers, operators, targets, tolerance):
    solutions = []
    
    # 1. Phân loại phép tính
    binary_ops_pool = [] # 2 ngôi: +, -, *, /, ^
    unary_ops_pool = []  # 1 ngôi: v, !
    
    for op in operators:
        if op in ['v', '!']:
            unary_ops_pool.append(op)
        else:
            binary_ops_pool.append(op)
            
    # --- CHECK LOGIC ---
    # Cần đúng 4 binary ops cho 5 số
    if len(binary_ops_pool) != 4:
        return None, "Lỗi: Để nối 5 số, bạn CẦN ĐÚNG 4 phép tính 2 ngôi (+ - * / ^). Các phép tính còn lại phải là 1 ngôi (v !)."

    # --- TẠO HOÁN VỊ ---
    num_perms = list(itertools.permutations(numbers))
    
    # Lấy hoán vị phép tính (loại bỏ trùng lặp nếu có phép tính giống nhau)
    bin_op_perms = list(set(itertools.permutations(binary_ops_pool)))

    # Xử lý phép tính Unary (nếu có 1 phép)
    # Nếu list unary rỗng, gán None để chạy loop 1 lần
    unary_op = unary_ops_pool[0] if unary_ops_pool else None
    
    seen_formulas = set()

    # --- VÒNG LẶP TÌM KIẾM ---
    for n_perm in num_perms:
        for b_perm in bin_op_perms:
            # Nếu có unary, thử gắn vào từng vị trí trong 5 số
            # Nếu không có unary, chỉ chạy loop 1 lần (range(1))
            range_positions = range(5) if unary_op else [None]
            
            for u_pos in range_positions:
                
                # Tạo list chuỗi số
                str_nums = [str(n) for n in n_perm]
                
                # Chèn Unary (nếu có)
                if u_pos is not None and unary_op:
                    if unary_op == 'v':
                        str_nums[u_pos] = f"math.sqrt({str_nums[u_pos]})"
                    elif unary_op == '!':
                        str_nums[u_pos] = f"math.factorial({str_nums[u_pos]})"
                
                # Chuyển đổi ký hiệu cho Python eval
                py_ops = [op.replace('^', '**') for op in b_perm]
                
                # Tạo chuỗi biểu thức Python
                expression = f"{str_nums[0]}{py_ops[0]}{str_nums[1]}{py_ops[1]}{str_nums[2]}{py_ops[2]}{str_nums[3]}{py_ops[3]}{str_nums[4]}"
                
                # Tạo chuỗi hiển thị đẹp
                display_ops = b_perm
                display_nums = [str(n) for n in n_perm]
                if u_pos is not None and unary_op == 'v': display_nums[u_pos] = f"√{n_perm[u_pos]}"
                elif u_pos is not None and unary_op == '!': display_nums[u_pos] = f"{n_perm[u_pos]}!"
                
                pretty_expr = f"{display_nums[0]} {display_ops[0]} {display_nums[1]} {display_ops[1]} {display_nums[2]} {display_ops[2]} {display_nums[3]} {display_ops[3]} {display_nums[4]}"

                if pretty_expr in seen_formulas: continue
                seen_formulas.add(pretty_expr)

                try:
                    # TÍNH TOÁN
                    val = eval(expression)
                    
                    if isinstance(val, complex): continue # Bỏ số phức
                    
                    # KIỂM TRA MỤC TIÊU
                    for t in targets:
                        diff = abs(val - t)
                        if diff <= tolerance:
                            solutions.append({
                                'val': val, 
                                'expr': pretty_expr, 
                                'diff': diff, 
                                'target': t
                            })
                            
                except (ValueError, ZeroDivisionError, OverflowError):
                    continue

    return solutions, None

# --- GIAO DIỆN CHÍNH ---
st.title("🧮 PEMDAS Solver: Tìm Số Thập Phân")
st.markdown("""
Tìm kiếm các biểu thức có kết quả **GẦN ĐÚNG** với mục tiêu (1 và 20).
""")

# Cột nhập liệu
with st.sidebar:
    st.header("Cấu hình")
    nums_in = st.text_input("5 Số (ngăn cách bởi dấu cách)", "3 5 2 8 1")
    ops_in = st.text_input("5 Phép tính", "+ * - ^ v")
    
    st.divider()
    
    # THANH TRƯỢT QUAN TRỌNG: ĐIỀU CHỈNH ĐỘ SAI SỐ
    st.markdown("**🎯 Độ chính xác**")
    tolerance = st.slider(
        "Sai số cho phép (+/-)", 
        min_value=0.0, 
        max_value=5.0, 
        value=1.5, 
        step=0.1,
        help="Ví dụ: Nếu chọn 1.5, mục tiêu là 20 sẽ chấp nhận kết quả từ 18.5 đến 21.5"
    )
    
    run_btn = st.button("🚀 Chạy Tìm Kiếm", type="primary")

# Xử lý Logic
if run_btn:
    try:
        # Parse Input
        clean_nums = nums_in.replace(',', ' ').split()
        nums = [int(x) if float(x).is_integer() else float(x) for x in clean_nums]
        
        clean_ops = ops_in.replace(',', ' ').split()
        ops = [x.strip() for x in clean_ops]
        
        if len(nums) != 5 or len(ops) != 5:
            st.error(f"Đang nhập: {len(nums)} số và {len(ops)} phép tính. Cần chính xác 5.")
        else:
            with st.spinner("Đang tính toán hàng nghìn khả năng..."):
                results, error = solve_pemdas(nums, ops, [1, 20], tolerance)
            
            if error:
                st.warning(error)
            elif not results:
                st.info(f"Không tìm thấy kết quả nào trong khoảng sai số +/- {tolerance}. Hãy thử tăng sai số lên.")
            else:
                # HIỂN THỊ KẾT QUẢ
                st.success(f"Tìm thấy {len(results)} phương án!")
                
                col1, col2 = st.columns(2)
                
                # --- HÀM HIỂN THỊ LIST ---
                def show_results(target_val, container):
                    subset = [r for r in results if r['target'] == target_val]
                    # Sắp xếp theo độ lệch nhỏ nhất trước
                    subset.sort(key=lambda x: x['diff'])
                    # Lấy Top 10
                    top_10 = subset[:10]
                    
                    if not top_10:
                        container.info("Không có kết quả phù hợp.")
                        return

                    for item in top_10:
                        # Logic màu sắc: Màu xanh nếu rất gần (<0.1), màu vàng nếu hơi xa
                        color = "green" if item['diff'] < 0.1 else "orange"
                        
                        container.markdown(f"""
                        <div style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                            <div style="font-size: 1.2em; font-weight: bold; color: #333;">
                                {item['expr']} 
                            </div>
                            <div style="display: flex; justify_content: space-between; align-items: center;">
                                <span style="font-size: 1.1em; color: {color}; font-weight: bold;">
                                    = {item['val']:.5f}
                                </span>
                                <span style="font-size: 0.9em; color: #666;">
                                    (Lệch: {item['diff']:.5f})
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                with col1:
                    st.header("🎯 Mục tiêu ~ 1")
                    show_results(1, col1)
                
                with col2:
                    st.header("🎯 Mục tiêu ~ 20")
                    show_results(20, col2)

    except Exception as e:
        st.error(f"Lỗi nhập liệu: {e}")
