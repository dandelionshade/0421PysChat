#!/usr/bin/env python
"""
测试运行脚本 - 执行全套或特定测试
用法: python scripts/run_tests.py [unit|integration|e2e|all]
"""
import sys
import subprocess
import os

def main():
    """主函数，运行测试"""
    # 确保在项目根目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 解析命令行参数
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    valid_types = ["unit", "integration", "e2e", "all"]
    
    if test_type not in valid_types:
        print(f"错误: 无效的测试类型 '{test_type}'")
        print(f"有效选项: {', '.join(valid_types)}")
        return 1
    
    # 确定要运行的测试目录
    if test_type == "all":
        test_path = "tests/"
    else:
        test_path = f"tests/{test_type}/"
    
    print(f"运行 {test_type} 测试...")
    
    # 运行pytest
    result = subprocess.run(
        ["python", "-m", "pytest", test_path, "-v"],
        check=False
    )
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
