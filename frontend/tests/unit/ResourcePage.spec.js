import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ResourcePage from '../../src/views/ResourcePage.vue'
import { ElMessage, ElCard, ElTag, ElForm, ElSelect, ElButton } from 'element-plus'

// 模拟API服务
vi.mock('../../src/services/api', () => ({
  default: {
    getResources: vi.fn()
  }
}))

// 模拟Element Plus组件
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn()
  }
}))

describe('ResourcePage.vue', () => {
  let wrapper;
  const mockResources = [
    {
      id: 1,
      title: "全国心理援助热线",
      description: "提供24小时心理支持和危机干预",
      category: "crisis",
      location_tag: "national",
      contact_info: "400-161-9995",
      url: "https://example.com/hotline"
    },
    {
      id: 2,
      title: "心理健康咨询中心",
      description: "提供专业心理咨询服务",
      category: "counseling",
      location_tag: "beijing",
      contact_info: "010-12345678",
      url: "https://example.com/center"
    }
  ];
  
  // 在每个测试之前重置组件
  beforeEach(() => {
    // 重置模拟函数
    const api = require('../../src/services/api').default;
    api.getResources.mockReset();
    
    wrapper = mount(ResourcePage, {
      global: {
        stubs: {
          ElCard: true,
          ElTag: true,
          ElForm: true,
          ElFormItem: true,
          ElSelect: true,
          ElOption: true,
          ElButton: true,
          ElEmpty: true
        }
      }
    });
  });

  it('初始化时加载资源', async () => {
    // 模拟API响应
    const api = require('../../src/services/api').default;
    api.getResources.mockResolvedValue({ data: mockResources });
    
    // 触发组件挂载后的资源加载
    await wrapper.vm.fetchResources();
    
    // 验证资源列表更新
    expect(wrapper.vm.resources.length).toBe(2);
    expect(api.getResources).toHaveBeenCalled();
  });

  it('过滤资源', async () => {
    // 模拟API响应
    const api = require('../../src/services/api').default;
    api.getResources.mockResolvedValue({ data: [mockResources[0]] });
    
    // 设置过滤值
    await wrapper.setData({
      filterForm: {
        category: 'crisis',
        location: 'national'
      }
    });
    
    // 触发筛选
    await wrapper.vm.fetchResources();
    
    // 验证API调用包含过滤参数
    expect(api.getResources).toHaveBeenCalledWith({
      category: 'crisis',
      location: 'national'
    });
  });

  it('重置过滤器', async () => {
    // 设置过滤值
    await wrapper.setData({
      filterForm: {
        category: 'crisis',
        location: 'national'
      }
    });
    
    // 重置过滤器
    await wrapper.vm.resetFilters();
    
    // 验证过滤值被清空
    expect(wrapper.vm.filterForm.category).toBe('');
    expect(wrapper.vm.filterForm.location).toBe('');
  });

  it('处理API错误', async () => {
    // 模拟API错误
    const api = require('../../src/services/api').default;
    api.getResources.mockRejectedValue(new Error('API错误'));
    
    // 触发资源加载
    await wrapper.vm.fetchResources();
    
    // 验证错误处理
    expect(ElMessage.error).toHaveBeenCalled();
  });
});
