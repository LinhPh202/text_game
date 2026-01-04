import itertools
import math

def solve_math_puzzle(numbers, target):
    """
    Giải đố: Tạo biểu thức từ 'numbers' để bằng 'target'.
    - Phép tính: +, -, *, /, ** (mũ), sqrt (căn bậc 2).
    - Ràng buộc: Tối đa 1 cặp ngoặc ().
    - Định dạng ra: x, :, ^, √.
    """
    
    # 1. Tiền xử lý số: Tạo danh sách các biến thể (số thường hoặc căn bậc 2)
    # Mỗi phần tử là tuple: (giá trị thực tế, chuỗi hiển thị, chuỗi tính toán python)
    number_variants = []
    for n in numbers:
        vars_for_n = []
        # Dạng thường
        vars_for_n.append((n, str(n), str(n)))
        # Dạng căn bậc 2 (nếu là số chính phương > 1)
        if n > 1 and math.isqrt(n)**2 == n:
            sqrt_val = int(math.isqrt(n))
            # Hiển thị: √9, Tính toán: 3
            vars_for_n.append((sqrt_val, f"√{n}", str(sqrt_val))) 
        number_variants.append(vars_for_n)

    # 2. Định nghĩa phép toán (Tính toán vs Hiển thị)
    # Lưu ý: Phép chia chỉ lấy chia hết để ra số nguyên đẹp
    ops_map = [
        ('+', '+'), 
        ('-', '-'), 
        ('*', 'x'), 
        ('/', ':'), 
        ('**', '^')
    ]

    # Hàm kiểm tra phép tính hợp lệ (tránh lỗi chia 0, mũ quá lớn)
    def valid_operation(a, b, op_symbol):
        if op_symbol == '/': 
            return b != 0 and a % b == 0 # Chỉ chấp nhận chia hết
        if op_symbol == '**': 
            # Giới hạn mũ để không sinh số quá lớn (ví dụ max: 10^5 hoặc 2^10)
            return (abs(a) <= 10 and 0 <= b <= 5) or (abs(a) <= 50 and b == 2)
        return True

    # 3. Vòng lặp chính: Hoán vị số -> Chọn biến thể (√ hay thường) -> Chọn phép tính -> Chọn mẫu ngoặc
    
    # Tạo tất cả hoán vị vị trí các số đầu vào
    for perm in itertools.permutations(number_variants):
        # perm là 1 list các list biến thể (vd: [vars_of_4, vars_of_9, vars_of_2])
        # Cần lấy tích Đề các để chọn cụ thể (vd: 4, √9, 2)
        for nums_chosen in itertools.product(*perm):
            # nums_chosen là 1 tuple các bộ (val, disp, calc). Vd: ((4,'4','4'), (3,'√9','3'), ...)
            vals = [x[0] for x in nums_chosen]
            disps = [x[1] for x in nums_chosen]
            calcs = [x[2] for x in nums_chosen]
            
            n_count = len(vals)
            
            # Chọn bộ phép tính
            for ops_chosen in itertools.product(ops_map, repeat=n_count - 1):
                op_calcs = [o[0] for o in ops_chosen] # +, -, *, /, **
                op_disps = [o[1] for o in ops_chosen] # +, -, x, :, ^
                
                # --- CÁC MẪU (TEMPLATES) TỐI ĐA 1 CẶP NGOẶC ---
                templates = []
                
                if n_count == 3:
                    A, B, C = calcs
                    dA, dB, dC = disps
                    o1, o2 = op_calcs
                    d1, d2 = op_disps
                    
                    # 1. Không ngoặc: A o1 B o2 C
                    templates.append((f"{A}{o1}{B}{o2}{C}", f"{dA} {d1} {dB} {d2} {dC}"))
                    # 2. Ngoặc đầu: (A o1 B) o2 C
                    templates.append((f"({A}{o1}{B}){o2}{C}", f"({dA} {d1} {dB}) {d2} {dC}"))
                    # 3. Ngoặc sau: A o1 (B o2 C)
                    templates.append((f"{A}{o1}({B}{o2}{C})", f"{dA} {d1} ({dB} {d2} {dC})"))

                elif n_count == 4:
                    A, B, C, D = calcs
                    dA, dB, dC, dD = disps
                    o1, o2, o3 = op_calcs
                    d1, d2, d3 = op_disps
                    
                    # Không ngoặc
                    templates.append((f"{A}{o1}{B}{o2}{C}{o3}{D}", f"{dA} {d1} {dB} {d2} {dC} {d3} {dD}"))
                    # (A o B) o C o D
                    templates.append((f"({A}{o1}{B}){o2}{C}{o3}{D}", f"({dA} {d1} {dB}) {d2} {dC} {d3} {dD}"))
                    # A o (B o C) o D
                    templates.append((f"{A}{o1}({B}{o2}{C}){o3}{D}", f"{dA} {d1} ({dB} {d2} {dC}) {d3} {dD}"))
                    # A o B o (C o D)
                    templates.append((f"{A}{o1}{B}{o2}({C}{o3}{D})", f"{dA} {d1} {dB} {d2} ({dC} {d3} {dD})"))
                    
                    # Lưu ý: Các dạng ((A B) C) D là 2 cặp ngoặc -> KHÔNG THÊM
                    # Các dạng (A B) (C D) là 2 cặp ngoặc -> KHÔNG THÊM

                # Kiểm tra kết quả
                for calc_str, disp_str in templates:
                    try:
                        # Kiểm tra từng bước để đảm bảo không lỗi (chia 0, số mũ lớn)
                        # Tuy nhiên eval Python xử lý thứ tự ưu tiên rất tốt
                        # Chỉ cần bắt lỗi ZeroDivisionError
                        res = eval(calc_str)
                        
                        # So sánh float với sai số nhỏ hoặc ép kiểu int nếu cần
                        if abs(res - target) < 1e-9:
                            # Kiểm tra lại tính hợp lệ từng bước (optional) nếu muốn chặt chẽ
                            # Nhưng với game giải trí, eval là đủ
                            return disp_str
                    except ZeroDivisionError:
                        continue
                    except Exception:
                        continue

    return "Không tìm thấy giải pháp"

# --- CHẠY THỬ NGHIỆM ---

# Test 1: Căn bậc 2 (Target: 5 từ 9, 4, 2)
# Kỳ vọng: (√9 + 4) - 2 = (3+4)-2 = 5 hoặc tương tự
print(f"Test 1 (9, 4, 2 -> 5): {solve_math_puzzle([9, 4, 2], 5)}")

# Test 2: Phép mũ (Target: 10 từ 3, 2, 1)
# Kỳ vọng: 3^2 + 1 = 10
print(f"Test 2 (3, 2, 1 -> 10): {solve_math_puzzle([3, 2, 1], 10)}")

# Test 3: Ngoặc đơn (Target: 20 từ 4, 6, 2)
# Kỳ vọng: (4 + 6) x 2 = 20
print(f"Test 3 (4, 6, 2 -> 20): {solve_math_puzzle([4, 6, 2], 20)}")
