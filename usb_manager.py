import sys
import ctypes
import winreg
import tkinter as tk
from tkinter import messagebox, simpledialog

# ================= 配置区 =================
# 请在这里设置你的解锁密码
UNLOCK_PASSWORD = "admin" 
# ==========================================

def is_admin():
    """检查当前是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 如果没有管理员权限，则自动重新以管理员身份运行
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv[1:]), None, 1)
    sys.exit()

def set_usb_status(disable=True):
    """
    修改注册表以启用或禁用 U 盘
    disable=True 禁用; disable=False 启用
    """
    try:
        # 方法 1：通过 Windows 组策略注册表禁用所有可移动存储（最安全，立即生效）
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\RemovableStorageDevices"
        try:
            # 创建或打开该路径
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
            # 1 为禁用所有访问，0 为解除限制
            winreg.SetValueEx(key, "Deny_All", 0, winreg.REG_DWORD, 1 if disable else 0)
            winreg.CloseKey(key)
        except Exception as e:
            print("GPO Registry Error:", e)

        # 方法 2：通过系统服务禁用 USBSTOR 大容量存储驱动（传统保险方法）
        usbstor_path = r"SYSTEM\CurrentControlSet\Services\USBSTOR"
        try:
            key2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, usbstor_path, 0, winreg.KEY_SET_VALUE)
            # 4 为禁用服务，3 为手动启动（默认）
            winreg.SetValueEx(key2, "Start", 0, winreg.REG_DWORD, 4 if disable else 3)
            winreg.CloseKey(key2)
        except Exception as e:
            print("USBSTOR Registry Error:", e)

        return True
    except Exception as e:
        messagebox.showerror("系统错误", f"修改注册表失败，请确保使用管理员身份运行。\n错误详情: {str(e)}")
        return False

def action_disable():
    if set_usb_status(disable=True):
        messagebox.showinfo("成功", "⛔ 所有 U 盘已被成功禁用！\n\n注意：已经插在电脑上的 U 盘拔出后再次插入将无法读取；鼠标、键盘不受影响。")

def action_enable():
    # 弹出密码输入框
    pwd = simpledialog.askstring("密码验证", "请输入解除限制的密码：", show='*')
    
    if pwd == UNLOCK_PASSWORD:
        if set_usb_status(disable=False):
            messagebox.showinfo("成功", "✅ 密码正确！U 盘已被解锁，现已恢复正常使用。")
    elif pwd is not None:  # is not None 表示用户没有点击取消
        messagebox.showerror("拦截", "❌ 密码错误，拒绝解锁！")

# ================= GUI 界面 =================
root = tk.Tk()
root.title("实验室 U 盘管理中心")
root.geometry("320x200")
root.resizable(False, False)

# 窗口居中
root.eval('tk::PlaceWindow . center')

lbl = tk.Label(root, text="请选择对本机 U 盘的操作：", font=("Microsoft YaHei", 12))
lbl.pack(pady=20)

btn_disable = tk.Button(root, text="⛔ 一键禁用 U 盘", bg="#ffcccc", font=("Microsoft YaHei", 10), width=20, height=2, command=action_disable)
btn_disable.pack(pady=5)

btn_enable = tk.Button(root, text="✅ 解锁 U 盘 (需密码)", bg="#ccffcc", font=("Microsoft YaHei", 10), width=20, height=2, command=action_enable)
btn_enable.pack(pady=5)

root.mainloop()
