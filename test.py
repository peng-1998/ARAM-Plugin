import pyautogui

# 获取当前鼠标的坐标
x, y = pyautogui.position()

# 获取窗口的坐标
window_title = "League of Legends"
window = pyautogui.getWindowsWithTitle(window_title)[0]
window_x, window_y = window.topleft

# 计算窗口内部的坐标
relative_x = x - window_x
relative_y = y - window_y

print("窗口坐标：", window_x, window_y)
print("鼠标坐标：", x, y)
print("相对坐标：", relative_x, relative_y)