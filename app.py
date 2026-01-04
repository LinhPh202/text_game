import streamlit as st
import math

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="Math Puzzle Solver", page_icon="🧮")

# --- HÀM XỬ LÝ TOÁN HỌC ---
def get_factorial(n):
    # Giới hạn giai thừa < 10 để tránh số quá lớn gây treo app
    if n < 0 or n > 10 or not math.isclose(n, int(n)):
        return None
    return math.factorial(int(n))

def get_sqrt(n):
    if n < 0: return None
    return math.sqrt(n)

def calculate(a, op, b=None):
    try:
        if op == '+': return a + b
        if op == '-': return a - b
        if op == '*': return a * b
        if op == '/': return a / b if b != 0 else None
        if op == '^': 
            # Giới hạn mũ để tránh overflow
            if abs(a) > 1000 and b > 2: return None
            if abs(b) > 10: return None 
            return a ** b
        if op == 'v': return get_sqrt(a)
        if op == '!': return get_factorial(a)
    except:
        return None
    return None

# --- HÀM ĐỆ QUY TÌM KIẾM ---
def solve_recursive(current_val, nums_left, ops_left, history, results):
    # Điều kiện dừng: Hết số và hết phép tính
    if not nums_left and not ops_left:
        results.append({
            'val': current_val,
            'path': history
        })
        return

    # Tối ưu: Nếu số lượng phép tính 2 ngôi (binary) nhiều hơn số lượng số còn lại -> Không thể giải -> Cắt nhánh sớm
    binary_ops_count = sum(1 for op in ops_left if op in ['+', '-', '*', '/', '^'])
    if binary_ops_count > len(nums_left):
        return

    unique_ops = set(ops_left)
    
    # 1. Thử phép tính 1 ngôi (Unary: v, !)
    for op in unique_ops:
        if op in ['v', '!']:
            new_val = calculate(current_val, op)
            if new_val is not None:
                new_ops = ops_left[:]
                new_ops.remove(op)
                solve_recursive(new_val, nums_left, new_ops, history + f" {op} → {new_val:.2f} |", results)

    # 2. Thử phép tính 2 ngôi (Binary: +, -, *, /, ^)
    if nums_left:
        for i, num in enumerate(set(nums_left)): 
            for op in unique_ops:
                if op in ['+', '-', '*', '/', '^']:
                    new_val = calculate(current_val, op, num)
                    if new_val is not None:
                        new_ops = ops_left[:]
                        new_ops.remove(op)
                        new_nums = nums_left[:]
                        new_nums.remove(num)
                        solve_recursive(new_val, new_nums, new_ops, history + f" {op} {num} → {new_val:.2f} |", results)

# --- GIAO DIỆN STREAMLIT ---
st.title("🧮 Thợ Giải Đố 5 Số - 5 Phép Tính")
st.markdown("""
Công cụ này giúp tìm cách kết hợp **5 con số** và **5 phép tính** để ra kết quả mong muốn.
Luật chơi: Không dùng ngoặc, tính tuần tự từ trái qua phải.
""")

with st.expander("ℹ️ Xem hướng dẫn nhập liệu"):
    st.markdown("""
    - **Phép tính hỗ trợ:** `+`, `-`, `*`, `/`, `^` (mũ), `v` (căn), `!` (giai thừa).
    - **Lưu ý:** `v` và `!` là phép tính 1 ngôi (tác động ngay lên số hiện tại).
    - Nhập các số và phép tính cách nhau bởi **dấu phẩy** hoặc **dấu cách**.
    """)

col1, col2 = st.columns(2)

with col1:
    input_nums_str = st.text_input("Nhập 5 số", "3, 5, 2, 8, 1")
    
with col2:
    input_ops_str = st.text_input("Nhập 5 phép tính", "+, *, -, v, ^")

target_1 = 1
target_2 = 20

# Nút bấm xử lý
if st.button("🚀 Tìm Lời Giải", type="primary"):
    # 1. Xử lý dữ liệu đầu vào
    try:
        # Làm sạch chuỗi input (thay dấu phẩy thành cách, rồi split)
        nums = [float(x) for x in input_nums_str.replace(',', ' ').split()]
        ops = [x.strip() for x in input_ops_str.replace(',', ' ').split()]
        
        if len(nums) == 0 or len(ops) == 0:
            st.error("Vui lòng nhập đủ số và phép tính.")
            st.stop()
            
    except ValueError:
        st.error("Lỗi định dạng số. Vui lòng kiểm tra lại.")
        st.stop()

    st.write(f"**Dữ liệu:** Số `{nums}` | Phép tính `{ops}`")
    
    # 2. Chạy thuật toán
    results = []
    
    progress_text = "Đang thử hàng nghìn trường hợp..."
    my_bar = st.progress(0, text=progress_text)
    
    # Bắt đầu duyệt (Loop qua từng số khởi đầu)
    total_start_nums = len(set(nums))
    for idx, start_num in enumerate(set(nums)):
        rem_nums = nums[:]
        rem_nums.remove(start_num)
        solve_recursive(start_num, rem_nums, ops, f"Bắt đầu: {start_num} |", results)
        # Cập nhật thanh tiến trình
        my_bar.progress(int((idx + 1) / total_start_nums * 100), text=progress_text)
        
    my_bar.empty() # Xóa thanh tiến trình khi xong

    if not results:
        st.warning("Không tìm thấy phép giải nào hợp lệ (Có thể do thiếu cân bằng giữa phép tính 1 ngôi và 2 ngôi).")
    else:
        # 3. Hiển thị kết quả
        st.divider()
        res_col1, res_col2 = st.columns(2)

        # -- KẾT QUẢ GẦN 1 --
        with res_col1:
            st.subheader(f"🎯 Mục tiêu: Gần {target_1}")
            results.sort(key=lambda x: abs(x['val'] - target_1))
            top_3_near_1 = results[:3]
            
            for i, sol in enumerate(top_3_near_1):
                diff = abs(sol['val'] - target_1)
                with st.container(border=True):
                    st.markdown(f"**Kết quả:** `{sol['val']:.4f}`")
                    st.caption(f"Độ lệch: {diff:.4f}")
                    st.code(sol['path'], language="text")

        # -- KẾT QUẢ GẦN 20 --
        with res_col2:
            st.subheader(f"🎯 Mục tiêu: Gần {target_2}")
            results.sort(key=lambda x: abs(x['val'] - target_2))
            top_3_near_20 = results[:3]
            
            for i, sol in enumerate(top_3_near_20):
                diff = abs(sol['val'] - target_2)
                with st.container(border=True):
                    st.markdown(f"**Kết quả:** `{sol['val']:.4f}`")
                    st.caption(f"Độ lệch: {diff:.4f}")
                    st.code(sol['path'], language="text")
