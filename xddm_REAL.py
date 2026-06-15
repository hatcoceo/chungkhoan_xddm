import pandas as pd

# =========================
# THAM SỐ CHIẾN LƯỢC
# =========================

P0 = 100          # giá mua ban đầu
q = 10            # số cổ phiếu mỗi lần mua
delta = 0.15      # ngưỡng +/-15%
n_steps = 20      # số lần mua tiếp theo

# Chuỗi quyết định:
# +1 = mua khi tăng 15%
# -1 = mua khi giảm 15%
#
# Ví dụ xen kẽ:
signals = [
    -1, +1, -1, -1, +1,
    +1, -1, +1, -1, +1,
    -1, -1, +1, -1, +1,
    -1, +1, -1, +1, -1
]

# =========================
# KHỞI TẠO
# =========================

prices = [P0]
avg_price = P0

total_shares = q
total_cost = P0 * q

records = []

records.append({
    "step": 0,
    "signal": 0,
    "buy_price": P0,
    "avg_price": avg_price,
    "shares": total_shares,
    "capital": total_cost
})

# =========================
# MÔ PHỎNG
# =========================

for i in range(n_steps):

    s = signals[i]

    # giá kích hoạt mua mới
    next_price = avg_price * (1 + s * delta)

    # mua thêm q cổ phiếu
    total_cost += next_price * q
    total_shares += q

    avg_price = total_cost / total_shares

    records.append({
        "step": i + 1,
        "signal": s,
        "buy_price": round(next_price, 4),
        "avg_price": round(avg_price, 4),
        "shares": total_shares,
        "capital": round(total_cost, 2)
    })

df = pd.DataFrame(records)

print(df)

print("\n===================")
print("KẾT QUẢ CUỐI")
print("===================")
print(f"Tổng cổ phiếu : {total_shares}")
print(f"Tổng vốn      : {total_cost:.2f}")
print(f"Giá vốn TB    : {avg_price:.4f}")