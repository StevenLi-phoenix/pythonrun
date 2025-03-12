#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import time
import sys
import platform
from datetime import datetime
from bleak import BleakScanner
from bleak.exc import BleakError
from typing import Dict, Any
from tqdm import tqdm

class BLEDeviceFinder:
    def __init__(self, scan_time: int = 60, rssi_threshold: int = -70):
        """
        初始化BLE设备查找器
        
        Args:
            scan_time: 扫描时间（秒）
            rssi_threshold: RSSI阈值，忽略信号强度小于此值的设备
        """
        self.scan_time = scan_time
        self.rssi_threshold = rssi_threshold
        self.first_scan_results: Dict[str, Any] = {}
        self.second_scan_results: Dict[str, Any] = {}
    
    async def check_bluetooth_status(self):
        """
        检查蓝牙状态
        
        Returns:
            bool: 蓝牙是否可用
        """
        try:
            # 尝试进行一次短暂的扫描来检查蓝牙状态
            await BleakScanner.discover(timeout=1.0)
            return True
        except BleakError as e:
            if "Bluetooth device is turned off" in str(e):
                print("\n错误: 蓝牙设备已关闭。请开启蓝牙后重试。")
            elif "Permission denied" in str(e) or "Access denied" in str(e):
                os_name = platform.system()
                if os_name == "Darwin":  # macOS
                    print("\n错误: 没有蓝牙权限。请在系统偏好设置中允许终端访问蓝牙。")
                elif os_name == "Windows":
                    print("\n错误: 没有蓝牙权限。请确保您已授予应用蓝牙权限。")
                elif os_name == "Linux":
                    print("\n错误: 没有蓝牙权限。请尝试使用sudo运行或将用户添加到bluetooth组。")
                else:
                    print(f"\n错误: 没有蓝牙权限。{e}")
            else:
                print(f"\n蓝牙错误: {e}")
            return False
        except Exception as e:
            print(f"\n检查蓝牙状态时出错: {e}")
            return False
    
    async def scan_devices(self) -> Dict[str, Any]:
        """
        扫描BLE设备
        
        Returns:
            包含设备信息的字典，键为设备地址
        """
        print(f"开始扫描BLE设备，持续{self.scan_time}秒...")
        print(f"将忽略信号强度(RSSI)小于{self.rssi_threshold}dBm的设备")
        start_time = time.time()
        end_time = start_time + self.scan_time
        
        devices = {}
        ignored_devices = 0
        
        # 创建进度条
        with tqdm(total=self.scan_time, desc="扫描进度", unit="秒", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
            last_update = 0
            
            while time.time() < end_time:
                current_time = time.time()
                elapsed = int(current_time - start_time)
                
                # 更新进度条
                if elapsed > last_update:
                    pbar.update(elapsed - last_update)
                    last_update = elapsed
                
                try:
                    # 执行扫描
                    discovered_devices = await BleakScanner.discover(timeout=2.0)
                    
                    # 更新设备列表
                    for device in discovered_devices:
                        # 直接获取RSSI属性
                        rssi = device.rssi if hasattr(device, 'rssi') else -100
                        
                        # 忽略信号强度小于阈值的设备
                        if rssi < self.rssi_threshold:
                            ignored_devices += 1
                            continue
                        
                        if device.address not in devices:
                            devices[device.address] = {
                                "name": device.name or "未知设备",
                                "address": device.address,
                                "rssi": rssi,
                                "first_seen": datetime.now().strftime("%H:%M:%S"),
                                "last_seen": datetime.now().strftime("%H:%M:%S"),
                                "seen_count": 1
                            }
                            # 在进度条下方显示新发现的设备
                            tqdm.write(f"发现新设备: {device.name or '未知设备'} ({device.address}) RSSI: {rssi}")
                        else:
                            devices[device.address]["last_seen"] = datetime.now().strftime("%H:%M:%S")
                            devices[device.address]["seen_count"] += 1
                            devices[device.address]["rssi"] = rssi  # 更新信号强度
                except BleakError as e:
                    tqdm.write(f"\n扫描过程中出现蓝牙错误: {e}")
                    tqdm.write("尝试继续扫描...")
                except Exception as e:
                    tqdm.write(f"\n扫描过程中出现未知错误: {e}")
                    tqdm.write("尝试继续扫描...")
                
                # 短暂休眠以减少CPU使用
                await asyncio.sleep(0.5)
            
            # 确保进度条完成
            pbar.update(self.scan_time - last_update)
        
        print(f"扫描完成，发现 {len(devices)} 个设备，忽略了 {ignored_devices} 个信号弱的设备")
        return devices
    
    async def run_first_scan(self):
        """执行第一次扫描"""
        print("=== 第一次扫描 ===")
        self.first_scan_results = await self.scan_devices()
        self.print_devices(self.first_scan_results)
    
    async def run_second_scan(self):
        """执行第二次扫描"""
        print("\n=== 第二次扫描 ===")
        self.second_scan_results = await self.scan_devices()
        self.print_devices(self.second_scan_results)
    
    def print_devices(self, devices: Dict[str, Any]):
        """打印设备列表"""
        if not devices:
            print("未发现设备")
            return
        
        print(f"{'设备名称':<30} {'MAC地址':<20} {'RSSI':<6} {'首次发现':<10} {'最后发现':<10} {'发现次数':<8}")
        print("-" * 90)
        
        for device in sorted(devices.values(), key=lambda x: x["rssi"], reverse=True):
            print(f"{device['name']:<30} {device['address']:<20} {device['rssi']:<6} "
                  f"{device['first_seen']:<10} {device['last_seen']:<10} {device['seen_count']:<8}")
    
    def compare_scans(self):
        """比较两次扫描的结果并显示差异，专注于出现/消失的设备"""
        if not self.first_scan_results or not self.second_scan_results:
            print("无法比较：缺少扫描数据")
            return
        
        print("\n=== 扫描结果比较 ===")
        
        # 获取设备地址集合
        first_addresses = set(self.first_scan_results.keys())
        second_addresses = set(self.second_scan_results.keys())
        
        # 找出新增的设备
        new_devices = second_addresses - first_addresses
        if new_devices:
            print("\n新增设备:")
            print(f"{'设备名称':<30} {'MAC地址':<20} {'RSSI':<6}")
            print("-" * 60)
            for addr in new_devices:
                device = self.second_scan_results[addr]
                print(f"{device['name']:<30} {device['address']:<20} {device['rssi']:<6}")
        else:
            print("\n没有新增设备")
        
        # 找出消失的设备
        disappeared_devices = first_addresses - second_addresses
        if disappeared_devices:
            print("\n消失的设备:")
            print(f"{'设备名称':<30} {'MAC地址':<20} {'RSSI':<6}")
            print("-" * 60)
            for addr in disappeared_devices:
                device = self.first_scan_results[addr]
                print(f"{device['name']:<30} {device['address']:<20} {device['rssi']:<6}")
        else:
            print("\n没有消失的设备")
        
        # 统计结果
        print(f"\n总结: 发现 {len(new_devices)} 个新增设备，{len(disappeared_devices)} 个消失的设备")


async def main():
    print("BLE设备查找器 - 查找并比较蓝牙低功耗设备")
    print("=" * 50)
    
    # 创建BLE设备查找器实例
    finder = BLEDeviceFinder(scan_time=60, rssi_threshold=-70)  # 扫描时间为60秒，忽略RSSI<-70的设备
    
    # 检查蓝牙状态
    if not await finder.check_bluetooth_status():
        print("\n请确保：")
        print("1. 蓝牙已开启")
        print("2. 应用有权限访问蓝牙")
        print("3. 蓝牙硬件正常工作")
        sys.exit(1)
    
    print("\n蓝牙状态正常，准备开始扫描...")
    
    try:
        # 第一次扫描
        await finder.run_first_scan()
        
        # 提示用户改变BLE设备状态
        print("\n请在接下来的10秒内改变您的BLE设备状态（开启/关闭等）...")
        for i in range(10, 0, -1):
            print(f"倒计时: {i}秒", end="\r")
            await asyncio.sleep(1)
        print("\n")
        
        # 第二次扫描
        await finder.run_second_scan()
        
        # 比较结果
        finder.compare_scans()
        
        print("\n扫描和比较完成！")
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except BleakError as e:
        print(f"\n蓝牙错误: {e}")
        print("请检查蓝牙设备状态和权限设置")
    except Exception as e:
        print(f"\n程序出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"\n程序出错: {e}") 