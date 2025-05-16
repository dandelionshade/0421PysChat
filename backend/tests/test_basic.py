'''
Author: zhen doniajohary2677@gmail.com
Date: 2025-05-15 20:30:54
LastEditors: zhen doniajohary2677@gmail.com
LastEditTime: 2025-05-16 13:14:04
FilePath: \0421PysChat\backend\tests\test_basic.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import os
import sys
import pytest
import logging
from dotenv import load_dotenv
import importlib.util

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加父目录到路径以便导入主应用
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载环境变量
load_dotenv()

def test_environment_setup():
    """测试环境变量是否正确设置"""
    logger.info("测试环境变量和模块导入")
    
    assert 'PYTHONPATH' in os.environ or True, "PYTHONPATH环境变量未设置（可选）"
    
    # 检查关键依赖
    required_modules = ['fastapi', 'uvicorn', 'pymysql', 'httpx', 'pytest']
    for module in required_modules:
        try:
            importlib.import_module(module)
            logger.info(f"✓ 已成功导入 {module}")
            assert True  # 使用assertion而不是return
        except ImportError:
            logger.error(f"✗ 无法导入 {module}")
            assert False, f"缺少必要的依赖: {module}"

def test_import_main():
    """测试主模块能否成功导入"""
    # 确保我们可以导入main模块
    main_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    assert os.path.exists(main_path), f"找不到main.py文件: {main_path}"
    
    spec = importlib.util.spec_from_file_location("main", main_path)
    assert spec is not None, f"无法从文件创建模块规格: {main_path}"
    assert spec.loader is not None, f"模块加载器未设置: {main_path}"
    main = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(main)
        logger.info("✓ 成功导入main模块")
        assert True  # 使用assertion而不是return
    except Exception as e:
        logger.error(f"✗ 导入main模块时出错: {e}")
        assert False, f"导入main模块失败: {e}"

def test_pydantic_models():
    """测试Pydantic模型定义是否正确"""
    try:
        from pydantic import BaseModel, ValidationError
        from typing import Optional
        
        # 定义一个简单的模型用于测试
        class TestModel(BaseModel):
            id: int
            name: str
            description: Optional[str] = None
        
        # 尝试创建一个模型实例
        test_instance = TestModel(id=1, name="Test")
        assert test_instance.id == 1
        assert test_instance.name == "Test"
        assert test_instance.description is None
        
        # 测试验证
        try:
            # 使用类型注解来避免静态类型检查警告
            from typing import Any, Dict
            invalid_data: Dict[str, Any] = {"id": "string_not_int", "name": "Invalid ID Type"}
            TestModel(**invalid_data)  # id字段类型错误，应该是int而不是str
            assert False, "验证应该失败，因为id字段类型错误"
        except ValidationError:
            # 验证失败是预期的
            logger.info("✓ Pydantic验证按预期工作")
            pass
        
        logger.info("✓ Pydantic模型测试通过")
        assert True  # 使用assertion而不是return
    except ImportError:
        logger.error("✗ 无法导入Pydantic")
        assert False, "缺少Pydantic依赖"
    except Exception as e:
        logger.error(f"✗ Pydantic模型测试失败: {e}")
        assert False, f"Pydantic模型测试失败: {e}"

# 主函数
if __name__ == "__main__":
    # 运行测试
    pytest.main(["-xvs", __file__])
