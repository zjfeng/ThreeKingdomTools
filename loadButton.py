import pyautogui
import time
import ctypes
import sys
import yaml
import os  # 新增：用于路径处理
from typing import Optional, Tuple
from pyautogui import ImageNotFoundException
from check_environment import EnvironmentChecker

class GameController:
    def __init__(self):
        # 加载配置（新增截图/滚动相关配置）
        self.config = self.load_config()
        self.confidence = self.config['automation']['confidence']
        self.assets_path = self.config['assets']['path']
        self.screenshot_path = self.config['screenshot']['path']  # 新增
        self.scroll_max_y = self.config['scroll']['max_y']  # 新增
        self.mouse_step = self.config['mouse']['step_y']  # 新增
        self.checks_passed = True
        self.error_messages = []
        
    def load_config(self) -> dict:
        """加载配置文件"""
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            sys.exit(1)
            
    def get_image_path(self, image_key: str) -> str:
        """获取图片完整路径"""
        return f"{self.assets_path}{self.config['assets']['images'][image_key]}"
        
    def check_assets_files(self) -> bool:
        """检查必要的资源文件是否存在"""
        required_files = self.config['assets']['images'].values()
        for file in required_files:
            try:
                with open(f"{self.assets_path}{file}", 'r'):
                    pass
            except:
                self.error_messages.append(f"缺少必要文件: {file}")
                self.checks_passed = False
        return self.checks_passed

    def check_screen_resolution(self) -> bool:
        """检查屏幕分辨率"""
        try:
            width, height = pyautogui.size()
            print(f"当前屏幕分辨率: {width}x{height}")
            min_width = self.config['screen']['min_width']
            min_height = self.config['screen']['min_height']
            if width < min_width or height < min_height:
                self.error_messages.append("屏幕分辨率过低")
                self.checks_passed = False
            return True
        except:
            self.error_messages.append("无法获取屏幕分辨率")
            self.checks_passed = False
            return False

    def wait_and_click(self, image_key: str, wait_time: float = None) -> bool:
        """等待并点击指定图片位置"""
        if wait_time is None:
            wait_time = self.config['automation']['wait_time']
            
        try:
            time.sleep(wait_time)
            image_path = self.get_image_path(image_key)
            print(f"正在查找图片: {image_path}")
            button_location = pyautogui.locateCenterOnScreen(
                image_path, 
                confidence=self.confidence
            )
            if button_location:
                print(f"找到图片位置: {button_location}")
                current_pos = pyautogui.position()
                print(f"当前鼠标位置: {current_pos}")
                
                pyautogui.moveTo(button_location, duration=0.5)
                print(f"移动鼠标到: {button_location}")
                
                time.sleep(0.5)
                pyautogui.click()
                print("执行点击操作")
                
                time.sleep(0.5)
                print(f"点击后鼠标位置: {pyautogui.position()}")
                
                return True
            print("未找到图片")
            return False
        except Exception as e:
            print(f"发生错误: {str(e)}")
            return False

    def click_relative_to_window(self, window_key: str) -> bool:
        """相对于游戏窗口点击指定位置"""
        window_path = self.get_image_path(window_key)
        window_region = pyautogui.locateOnScreen(
            window_path, 
            confidence=self.confidence
        )
        if window_region:
            offset_x = self.config['automation']['click_offset']['x']
            offset_y = self.config['automation']['click_offset']['y']
            click_x = window_region.left + offset_x
            click_y = window_region.top + offset_y
            pyautogui.click(click_x, click_y)
            return True
        return False

    def capture_screenshot(self, filename: str) -> bool:  # 新增方法
        """截图并保存到配置路径"""
        try:
            os.makedirs(self.screenshot_path, exist_ok=True)  # 自动创建目录
            filepath = os.path.join(self.screenshot_path, f"{filename}.png")
            pyautogui.screenshot(filepath)
            print(f"截图已保存到: {filepath}")
            return True
        except Exception as e:
            print(f"截图失败: {str(e)}")
            return False

def main():
    try:
        controller = GameController()
        environment_checker = EnvironmentChecker()
        if not environment_checker.run_all_checks():
            print("环境检查未通过，程序退出")
            return
            
        print("\n开始执行自动化操作...")
        
        # 点击武将1
        if not controller.wait_and_click('wujiang1'):
            print("点击武将1失败")
            return
        else:
            print("点击武将按钮1")
            
        # 点击武将2
        if not controller.wait_and_click('wujiang2'):
            print("点击武将2失败")
            return
        else:
            print("点击武将按钮2")
            
        # 首次进入武将详情
        if not controller.click_relative_to_window('game_window'):
            print("首次点击武将详情失败")
            return
        else:
            # 初始化循环变量（修改部分）
            position = pyautogui.position()
            processed_heroes = 0  # 已处理的武将计数器
            max_heroes = controller.config['heroes']['total']  # 从配置获取总武将数

            print(f"鼠标初始位置，坐标: ({position.x}, {position.y})")

            while processed_heroes < max_heroes:  # 循环条件改为未超过总武将数
                # 截图（带时间戳避免覆盖）
                timestamp = time.strftime("%Y%m%d%H%M%S")
                if not controller.capture_screenshot(f"detail_{timestamp}"):
                    print("截图失败，终止流程")
                    break

                processed_heroes += 1  # 每成功截图1次，计数器+1
                print(f"已处理武将：{processed_heroes}/{max_heroes}")

                # 返回上一层
                if not controller.wait_and_click('back_button'):
                    print("返回按钮未找到，终止流程")
                    break

                # 鼠标移动回指定初始位置（原鼠标下移逻辑修改）
                pyautogui.moveTo(position.x, position.y, duration=0.5)  # 移动到初始位置（带平滑动画）
                print(f"鼠标已移动回初始位置，坐标: ({position.x}, {position.y})")

                # 滚轮向下滚动
                pyautogui.scroll(-100)  # 向下滚动一格
                print("滚轮向下滚动一格")
                time.sleep(1)  # 等待滚动动画

                # 再次进入武将详情
                pyautogui.click()
                print("再次点击武将详情失败")

            print(f"已处理所有{max_heroes}个武将，循环结束")
        print("自动化操作完成")
        
    except Exception as e:
        print(f"程序执行出错: {str(e)}")
        
    finally:
        # 无论程序如何结束，都执行返回操作
        print("\n执行返回操作...")
        try:
            while True:
                # 尝试返回操作，最多尝试3次
                if not controller.wait_and_click('back_button'):
                    break
                print("成功执行一次返回操作")
                time.sleep(0.5)
        except Exception as e:
            print(f"返回操作失败: {str(e)}")
        finally:
            print("返回操作流程结束")

if __name__ == '__main__':
    main()