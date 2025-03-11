import cv2 
import numpy as np
import sys
import os

print(sys.argv)

blank = np.zeros((400, 400), dtype=np.uint8)
blank[:200, :200] = int(sys.argv[1]) % 255

# 创建一个空白图像
blank = np.zeros((400, 400), dtype=np.uint8)
blank[:200, :200] = int(sys.argv[1]) % 255

# 使用cv2在图像上绘制一个矩形
cv2.rectangle(blank, (50, 50), (150, 150), (255, 0, 0), -1)

# 保存图像到临时文件
temp_filename = "temp_image.png"
cv2.imwrite(temp_filename, blank)

# 读取图像并检查矩形是否存在
loaded_image = cv2.imread(temp_filename, cv2.IMREAD_GRAYSCALE)
assert loaded_image[100, 100] == 255, "矩形未正确绘制"

# 删除临时文件
os.remove(temp_filename)


print("测试完成")