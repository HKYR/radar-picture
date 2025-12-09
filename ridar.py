import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# --------------------------
# 1. 原始 11 维数据
# --------------------------
data_configs = [
    ("1 scale (8-th)",
     [91, 84, 81, 76, 78, 82, 86, 89, 87, 88, 85],  # Seen
    #  [50,55,60,65,70,75,80,85,90,95,100],  # Seen
     [86, 81, 79, 78, 78, 80, 82, 83, 81, 80, 81],  # Unseen
     '#4C72B0'),
    ("3 scales (6-th, 8-th, 10-th)",
     [95, 86, 82, 80, 78, 83, 89, 92, 90, 91, 93],  # Seen
     [90, 84, 83, 82, 80, 84, 84, 85, 87, 83, 88],  # Unseen
     '#DD8452'),
    ("7 scales (5-th ~ 11-th)",
     [88, 81, 81, 79, 78, 79, 82, 83, 86, 85, 82],  # Seen
     [87, 79, 76, 76, 77, 80, 80, 81, 82, 83, 85],  # Unseen
     '#55A868'),
    ("10 scales (3-rd ~ 13-th)",
     [94, 88, 86, 85, 87, 88, 90, 89, 90, 86, 91],  # Seen
     [86, 81, 81, 79, 78, 81, 81, 80, 82, 81, 82],  # Unseen
     '#C44E52'),
]
# 函数：对数据进行减去50再乘以2
def modify_data(data):
    return [(x - 50) * 2 for x in data]

# 对数据进行修改
modified_data_configs = []
for name, seen, unseen, color in data_configs:
    modified_seen = modify_data(seen)
    modified_unseen = modify_data(unseen)
    modified_data_configs.append((name, modified_seen, modified_unseen, color))


# --------------------------
# 2. 5 维 → 11 维：使用周期插值（保证首尾相接）
# --------------------------
def interpolate_to_11_periodic(values):
    values = np.asarray(values)
    x_old = np.linspace(0, 2*np.pi, len(values) + 1)
    y_old = np.append(values, values[0])  # 首尾闭合

    x_new = np.linspace(0, 2*np.pi, 11, endpoint=False)
    y_new = np.interp(x_new, x_old, y_old)
    return y_new

interp_data_configs = []
for name, seen, unseen, color in modified_data_configs:
    seen_11   = interpolate_to_11_periodic(seen)
    unseen_11 = interpolate_to_11_periodic(unseen)
    interp_data_configs.append((name, seen_11, unseen_11, color))

# --------------------------
# 3. 11 维雷达角度（全局统一使用这套角度）
# --------------------------
num_dims = 11
angles = np.linspace(0, 2*np.pi, num_dims, endpoint=False)
angles_closed = np.concatenate([angles, angles[:1]])  # 封闭一圈用

# --------------------------
# 4. 画图设置
# --------------------------
fig, ax = plt.subplots(figsize=(16, 16), subplot_kw=dict(polar=True))

ax.set_theta_direction(-1)  # 顺时针方向

# --------------------------
# 5. 色块：拆分成 2 个色块，并对齐
# --------------------------
# sector_colors = ['#D6EAF8', '#F4ECF7', '#FADBD8', '#FCF3CF', '#D6EAF8']
sector_sizes = [5, 6]  # 只保留两个色块
sector_colors = [
    '#A2C6E4',   # 蓝色
    '#E6D29F',   # 紫色
]

# 11 个边界角度
boundary_angles = np.linspace(0, 2*np.pi, 11 + 1)

# 额外旋转偏移 Δθ = 2π/28 = π/14
theta_shift = 0
r_outer = 100
start_idx = 0
for color, size in zip(sector_colors, sector_sizes):

    end_idx = start_idx + size

    theta1 = (boundary_angles[start_idx] + theta_shift) % (2*np.pi)
    theta2 = (boundary_angles[end_idx] + theta_shift) % (2*np.pi)

    wedge = Wedge(
        (0, 0),
        r_outer,
        np.degrees(theta1),
        np.degrees(theta2),
        transform=ax.transData._b,
        color=color,
        alpha=0.5,
        zorder=0
    )
    ax.add_patch(wedge)

    start_idx = end_idx

# --------------------------
# 6. 径向刻度与同心圆（改成 10 个，均匀间距）
# --------------------------
                # 保持最外圈半径不变
num_circles = 10              # 10 个同心圆
radial_ticks = np.linspace(r_outer / num_circles, r_outer, num_circles)

ax.set_ylim(0, r_outer)
ax.set_yticks(radial_ticks)
ax.set_yticklabels([])

for r in radial_ticks:
    lw = 1.5  # 所有径向线宽度一致
    circle = plt.Circle(
        (0, 0), r,
        transform=ax.transData._b,
        fill=False, edgecolor='white',
        linewidth=lw, alpha=0.7, zorder=1
    )
    ax.add_patch(circle)

# --------------------------
# 7. 绘制 11 维插值后的数据
# --------------------------
for name, seen_11, unseen_11, color in interp_data_configs:
    seen_closed   = np.concatenate([seen_11,   [seen_11[0]]])
    unseen_closed = np.concatenate([unseen_11, [unseen_11[0]]])

    # Seen
    ax.plot(angles_closed, seen_closed, '-', 
            linewidth=1.5, color=color,  # 折线变细
            label=f"{name} (Seen Object)", zorder=5)
    ax.fill(angles_closed, seen_closed, 
            alpha=0.20, color=color, zorder=2)
    ax.plot(angles, seen_11, 'o', color='#B0B0B0',  # 顶点变为浅灰色
            markersize=5, zorder=4)  # 圆点的 zorder 调整为 4，位于折线下方

    # Unseen
    ax.plot(angles_closed, unseen_closed, '--',
            linewidth=1.5, color=color,  # 虚线变细，linewidth 设置为 1.5
            label=f"{name} (Unseen Object)", dashes=(5, 3), zorder=5)
    ax.plot(angles, unseen_11, 'o', color='#B0B0B0',  # 顶点变为浅灰色
            markersize=5, zorder=4)  # 圆点的 zorder 调整为 4，位于折线下方


# --------------------------
# 8. 11 条径向线（保持粗细一致）
# --------------------------
for angle in angles:
    # print(angle)
    ax.vlines(angle, 0, r_outer, alpha=0.3, color='gray', linewidth=1.5)  # 所有径向线宽度一致
ax.vlines(0, 0, r_outer, alpha=0.8, color='black', linewidth=2)
ax.set_xticks(angles)
ax.set_xticklabels([''] * num_dims)

ax.grid(True, axis='x', linestyle='-',
        linewidth=1.0, alpha=0.3, color='gray', zorder=1)
ax.spines['polar'].set_visible(False)

# --------------------------
# 9. 图例
# --------------------------
ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1.05),
          fontsize=11, framealpha=0.95, edgecolor='black')

plt.tight_layout()
plt.show()
