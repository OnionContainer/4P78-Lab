import time
import tkinter as tk
from typing import List, Tuple


"""

graphic here, interactive in coordinateDrawer

"""

class MyTk(tk.Tk):
    def __init__(self, width=1000, height=700):
        super().__init__()
        print("no?")

        self.title("Arms")
        self.width = width
        self.height = height

        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        self.canvas.create_line(self.width // 2, 0, self.width // 2, self.height, fill="black")  # Y-axis
        self.canvas.create_line(0, self.height // 2, self.width, self.height // 2, fill="black")  #
        self.sign_point((-105,115), "origin", "object location", (0,30))
        # # 扇形测试，从 -30° 开始
        # x, y = 200, 200  # 圆心坐标
        # r = 100  # 半径
        # self.canvas.create_arc(x - r, y - r, x + r, y + r,
        #                   start=-30, extent=10, outline="red", width=2)

    def clear_fans(self):
        self.canvas.delete("fan")

    def draw_fan_contour(self, x, y, radius, start_angle, extent, outline_color, width):
        """
        在 Tkinter Canvas 上绘制一个扇形轮廓（无填充，只有边）。

        :param x: 圆心的 x 坐标
        :param y: 圆心的 y 坐标
        :param radius: 圆的半径
        :param start_angle: 开始的角度（以度为单位，从3点钟位置逆时针计算）is timed -1 inside this function
        :param extent: 扇形的角度范围（即绘制多少度）
        :param outline_color: 轮廓颜色
        :param width: 轮廓的线宽
        """
        # 定义边界框：左上角 (x - r, y - r), 右下角 (x + r, y + r)
        x,y = self.coordinate_centering_filter((x,y))
        x0, y0 = x - radius, y - radius
        x1, y1 = x + radius, y + radius

        start_angle *= -1
        extent *= -1

        # 使用 create_arc 绘制扇形轮廓
        self.canvas.create_arc(
            x0, y0, x1, y1,
            start=start_angle,  # 起始角度
            extent=extent,  # 绘制范围
            outline=outline_color,  # 轮廓颜色
            fill='',  # 无填充
            width=width,# 线宽
            tags="fan"
        )

    def coordinate_centering_filter(self, point:Tuple[float,float])->Tuple[float,float]:

        x_shift = self.width // 2.0
        y_shift = self.height // 2.0

        return point[0] + x_shift, point[1] + y_shift

    def sign_point(self, point, tag="point", message=None, shift=None):
        self.sign_points([point], tag, message, shift)

    def sign_points(self, points: List[Tuple[float, float]], tag="point", message = None, shift=None):
        """
        Draw the given points on the canvas.
        :param points: List of (x, y) tuples representing points to draw
        """
        # Clear the canvas first
        # self.canvas.delete("point")  # Line commented to retain previously drawn points

        for x, y in points:
            # Store the point data for reference or future use
            # Adjust points to canvas coordinates (centered at the middle)
            # x,y = self.coordinate_centering_filter((x,y))
            # canvas_x = self.width // 2 + x
            # canvas_y = self.height // 2 - y

            canvas_x,canvas_y = self.coordinate_centering_filter((x,y))

            # Draw the point (a small oval)
            self.canvas.create_oval(
                canvas_x - 5, canvas_y - 5, canvas_x + 5, canvas_y + 5,
                fill="#f03099", outline="#000000", tags=tag
            )

            self.canvas.create_text(
                canvas_x + 10 if shift is None else canvas_x + shift[0],
                canvas_y - 15 if shift is None else canvas_y + shift[1],
                text=f"({x:.1f}, {y:.1f})" if message is None else message,
                fill="red",
                tags=tag,
                font = ("Arial", 10),  # Font & size
            )

        # Update the canvas
        self.canvas.update()

    def sign_line(self, point1=(0.0,0.0), point2=(1.0,1.0)):
        #draw a line from point 1 to point 2
        # self.canvas.delete("line")
        point1 = self.coordinate_centering_filter(point1)
        point2 = self.coordinate_centering_filter(point2)
        self.canvas.create_line(point1, point2, fill="red", tags="line")
        pass

    def clear_canvas(self, tag=None):
        if tag is not None:
            self.canvas.delete(tag)
        else:
            self.canvas.delete("point")
            self.canvas.delete("line")

if __name__ == "__main__":

    mytk = MyTk()
    mytk.sign_point((0,0))
    mytk.mainloop()

