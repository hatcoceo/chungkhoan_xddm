
class DynamicLimitGridStrategy:
    def __init__(
        self,
        first_price: float,
        alpha: float = 0.15,
        buy_size: float = 100,
        eps_ratio: float = 0.0005
    ):
        self.alpha = alpha
        self.buy_size = buy_size
        self.eps_ratio = eps_ratio

        # Trạng thái vốn
        self.total_qty = buy_size
        self.total_cost = first_price * buy_size
        self.avg_price = first_price
        self.buy_count = 1

        # Lệnh chờ
        self.pending_orders = {}

        # Lịch sử
        self.history = [{
            "buy_no": 1,
            "price": first_price,
            "avg_price": self.avg_price,
            "total_qty": self.total_qty,
            "total_cost": self.total_cost,
            "side": "init"
        }]

        self.place_limit_orders()

    # ==============================
    # ĐẶT LỆNH CHỜ
    # ==============================
    def place_limit_orders(self):
        self.pending_orders = {
            "down": self.avg_price * (1 - self.alpha),
            "up":   self.avg_price * (1 + self.alpha)
        }

    # ==============================
    # UPDATE GIÁ
    # ==============================
    def on_price_update(self, market_price: float):
        eps = self.avg_price * self.eps_ratio

        for side, target_price in self.pending_orders.items():
            if abs(market_price - target_price) <= eps:
                self.execute_buy(target_price, side)
                break

    # ==============================
    # EXECUTE BUY
    # ==============================
    def execute_buy(self, buy_price: float, side: str):
        self.buy_count += 1
        self.total_qty += self.buy_size
        self.total_cost += buy_price * self.buy_size
        self.avg_price = self.total_cost / self.total_qty

        self.history.append({
            "buy_no": self.buy_count,
            "price": buy_price,
            "avg_price": self.avg_price,
            "total_qty": self.total_qty,
            "total_cost": self.total_cost,
            "side": side
        })

        self.place_limit_orders()

    # ==============================
    # IN LỊCH SỬ
    # ==============================
    def print_history(self):
        print("\n=== LỊCH SỬ KHỚP LỆNH ===")
        for h in self.history:
            print(
                f"Lần {h['buy_no']:>2} | "
                f"{h['side']:>5} | "
                f"Giá mua: {h['price']:>8.4f} | "
                f"Giá vốn: {h['avg_price']:>8.4f} | "
                f"Tổng SL: {h['total_qty']:>6}"
            )

    # ==============================
    # THỐNG KÊ CƠ BẢN
    # ==============================
    def count_up_down(self):
        up = sum(1 for h in self.history if h["side"] == "up")
        down = sum(1 for h in self.history if h["side"] == "down")
        return up, down

    # ==============================
    # HỆ SỐ UP/DOWN
    # ==============================
    def up_down_ratio(self):
        up, down = self.count_up_down()
        if down == 0:
            return float('inf')
        return up / down

    def up_down_score(self):
        up, down = self.count_up_down()
        total = up + down
        if total == 0:
            return 0
        return (up - down) / total

    # ==============================
    # ĐỘ ZIGZAG (FLIP RATE)
    # ==============================
    def flip_rate(self):
        sides = [h["side"] for h in self.history if h["side"] in ("up", "down")]

        flips = 0
        for i in range(1, len(sides)):
            if sides[i] != sides[i - 1]:
                flips += 1

        if len(sides) <= 1:
            return 0

        return flips / (len(sides) - 1)

    # ==============================
    # ĐỘ DÀI TREND
    # ==============================
    def avg_streak_length(self):
        sides = [h["side"] for h in self.history if h["side"] in ("up", "down")]

        if not sides:
            return 0

        streaks = []
        current = 1

        for i in range(1, len(sides)):
            if sides[i] == sides[i - 1]:
                current += 1
            else:
                streaks.append(current)
                current = 1

        streaks.append(current)
        return sum(streaks) / len(streaks)

    # ==============================
    # TỔNG KẾT
    # ==============================
    def summary(self):
        up, down = self.count_up_down()

        print("\n=== TỔNG KẾT ===")
        print(f"Số lần mua: {self.buy_count}")
        print(f"Tổng khối lượng: {self.total_qty}")
        print(f"Tổng vốn: {self.total_cost:.2f}")
        print(f"Giá vốn trung bình: {self.avg_price:.4f}")

        print("\n--- Up/Down ---")
        print(f"Up: {up}")
        print(f"Down: {down}")
        print(f"Ratio: {self.up_down_ratio():.4f}")
        print(f"Score: {self.up_down_score():.4f}")

        print("\n--- Market Structure ---")
        print(f"Flip rate: {self.flip_rate():.4f}")
        print(f"Avg streak: {self.avg_streak_length():.4f}")

        print("\n--- Pending Orders ---")
        for k, v in self.pending_orders.items():
            print(f"{k}: {v:.4f}")
strategy = DynamicLimitGridStrategy(
    first_price=100,
    alpha=0.15,
    buy_size=100
)

market_prices = [
    95, 90, 85,
    80, 79, 78.6,
    78.625,
    90, 100, 106.4
]

for price in market_prices:
    strategy.on_price_update(price)

strategy.print_history()
strategy.summary()
