from typing import List
from crypto_dot_com.asciichartpy import plot

MAX_HEIGHT = 12


def gen_ascii_plot(points: List[float], height=MAX_HEIGHT) -> str:
    output = plot(
        series=points,
        cfg={
            "height": height,
            "offset": 1,
        },
    )
    x_axis = ""
    interval = 6
    n = len(points)
    for i in range(1, n // interval + 1):
        x_axis += "{: >{}}".format(str(i * interval)[::-1], interval)
    output += "\n" + "{: >{}}".format(x_axis[::-1], n)
    min_value = min(points)
    max_value = max(points)
    percentage_diff = (max_value - min_value) / min_value * 100
    output += f"\n${min_value:,.2f} - ${max_value:,.2f} (%{percentage_diff:.2f})"
    return output


def _gen_ascii_plot(points: List[float]) -> str:
    n = len(points)
    if n <= 1:
        return ""

    grid = [[" "] * n for _ in range(MAX_HEIGHT)]

    max_value = max(points)
    min_value = min(points)
    interval = (max_value - min_value) / (MAX_HEIGHT - 1)

    def get_j(point):
        btm_up_i = -1
        curr_val = min_value - interval / 2
        while point > curr_val:
            btm_up_i += 1
            curr_val += interval
        return MAX_HEIGHT - 1 - btm_up_i

    for i, point in enumerate(points):
        j = get_j(point)
        grid[j][i] = "*"

    output = f"^ ${max_value:,.2f}"
    for row in grid:
        output += "\n|" + "".join(row)
    output += f"\n| ${min_value:,.2f}"
    output += "\n" + "-" * n + ">"

    return output
