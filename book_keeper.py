import os
from datetime import datetime


class BookKeeper:

    def __init__(self, trial_number):
        """初始化类，自动创建日志文件名并打开文件供写入"""
        self.trial_number = trial_number  # 试验编号
        os.makedirs("log", exist_ok=True)
        self.log_file_name = f"log/trial_{trial_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"  # 文件名
        self.log_file = open(self.log_file_name, "w")  # 打开文件用于写入
        print(f"Log file created: {self.log_file_name}")  # 提示文件的创建

    def print_log(self, message):
        """将日志消息写入文件并打印到屏幕"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # 添加时间戳
        log_entry = f"[{timestamp}] {message}"  # 日志条目格式
        print(log_entry)  # 打印到控制台
        self.log_file.write(log_entry + "\n")  # 写入文件

    def close(self):
        """关闭日志文件"""
        self.log_file.close()
        print(f"Log file {self.log_file_name} closed.")


# 使用示例
if __name__ == "__main__":
    trial_number = 1
    book_keeper = BookKeeper(trial_number)

    # 添加一些日志记录
    book_keeper.print_log("Trial started.")
    book_keeper.print_log("Performing some task...")
    book_keeper.print_log("Trial completed successfully.")

    # 关闭日志文件
    book_keeper.close()