import pyautogui
import ctypes
import sys
import yaml
import time

class EnvironmentChecker:
    def __init__(self, config_path='config.yaml'):
        self.config = self.load_config(config_path)
        self.assets_path = self.config['assets']['path']
        self.required_images = self.config['assets']['images']
        self.min_width = self.config['screen']['min_width']
        self.min_height = self.config['screen']['min_height']
        self.checks_passed = True
        self.error_messages = []

    def load_config(self, config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            sys.exit(1)

    def check_admin_rights(self):
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                self.error_messages.append("需要管理员权限运行")
                self.checks_passed = False
            return is_admin
        except:
            self.error_messages.append("无法检查管理员权限")
            self.checks_passed = False
            return False

    def check_screen_resolution(self):
        try:
            width, height = pyautogui.size()
            print(f"当前屏幕分辨率: {width}x{height}")
            if width < self.min_width or height < self.min_height:
                self.error_messages.append(f"屏幕分辨率过低，需至少{self.min_width}x{self.min_height}")
                self.checks_passed = False
            return True
        except:
            self.error_messages.append("无法获取屏幕分辨率")
            self.checks_passed = False
            return False

    def check_assets_files(self):
        for key, file in self.required_images.items():
            try:
                with open(f"{self.assets_path}{file}", 'r'):
                    pass
            except:
                self.error_messages.append(f"缺少必要文件: {file}（键名：{key}）")
                self.checks_passed = False
        return self.checks_passed

    def test_mouse_control(self):
        try:
            start_pos = pyautogui.position()
            print(f"当前鼠标位置: {start_pos}")
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            pyautogui.moveTo(center_x, center_y, duration=1)
            pyautogui.click()
            pyautogui.moveTo(start_pos, duration=1)
            return True
        except:
            self.error_messages.append("鼠标控制测试失败")
            self.checks_passed = False
            return False

    def test_image_recognition(self):
        try:
            screenshot = pyautogui.screenshot()
            test_path = f"{self.assets_path}{self.required_images.get('test_screenshot', 'test_screenshot.png')}"
            screenshot.save(test_path)
            print("屏幕截图测试成功")
            return True
        except:
            self.error_messages.append("图像识别测试失败")
            self.checks_passed = False
            return False

    def run_all_checks(self):
        print("开始运行自动化环境检查...")

        checks = [
            ("管理员权限检查", self.check_admin_rights),
            ("屏幕分辨率检查", self.check_screen_resolution),
            ("资源文件检查", self.check_assets_files),
            ("鼠标控制测试", self.test_mouse_control),
            ("图像识别测试", self.test_image_recognition)
        ]

        for check_name, check_func in checks:
            print(f"\n执行{check_name}...")
            check_func()

        if self.checks_passed:
            print("\n所有检查通过！可以开始自动化操作。")
        else:
            print("\n检查未通过，存在以下问题：")
            for error in self.error_messages:
                print(f"- {error}")

        return self.checks_passed

def main():
    # 如果不是管理员，则请求管理员权限重新运行
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    checker = EnvironmentChecker()
    checker.run_all_checks()

if __name__ == '__main__':
    main()
