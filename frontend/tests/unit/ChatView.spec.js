import { mount } from '@vue/test-utils'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ChatView from '../../src/views/ChatView.vue'
import { ElMessage, ElInput, ElButton } from 'element-plus'

// 模拟API服务
vi.mock('../../src/services/api', () => ({
  default: {
    sendMessage: vi.fn()
  }
}))

// 模拟Element Plus组件
vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn()
  }
}))

describe('ChatView.vue', () => {
  let wrapper;
  
  // 在每个测试之前重置组件
  beforeEach(() => {
    wrapper = mount(ChatView, {
      global: {
        stubs: {
          ElInput: true,
          ElButton: true,
          ElIcon: true
        }
      }
    });
  });

  it('初始化时有欢迎消息', () => {
    const messages = wrapper.findAll('.message');
    expect(messages.length).toBe(1);
    expect(messages[0].classes()).toContain('assistant');
  });

  it('当输入为空时禁用发送按钮', async () => {
    const sendButton = wrapper.findComponent(ElButton);
    expect(sendButton.attributes('disabled')).toBeDefined();
  });

  it('发送消息后清空输入框', async () => {
    // 设置输入值
    await wrapper.setData({ userInput: '你好，这是一个测试' });
    
    // 模拟API响应
    const mockApiResponse = {
      data: { response: '你好，我是心理助手' }
    };
    
    const api = require('../../src/services/api').default;
    api.sendMessage.mockResolvedValue(mockApiResponse);
    
    // 触发发送消息
    await wrapper.vm.sendMessage();
    
    // 验证输入框被清空
    expect(wrapper.vm.userInput).toBe('');
    
    // 验证消息列表更新
    expect(wrapper.vm.messages.length).toBe(3); // 欢迎消息 + 用户消息 + 回复
    expect(wrapper.vm.messages[1].role).toBe('user');
    expect(wrapper.vm.messages[2].role).toBe('assistant');
  });

  it('处理API错误', async () => {
    // 设置输入值
    await wrapper.setData({ userInput: '测试错误处理' });
    
    // 模拟API错误
    const api = require('../../src/services/api').default;
    api.sendMessage.mockRejectedValue(new Error('API错误'));
    
    // 触发发送消息
    await wrapper.vm.sendMessage();
    
    // 验证错误处理
    expect(ElMessage.error).toHaveBeenCalled();
    
    // 验证错误消息被添加
    const lastMessage = wrapper.vm.messages[wrapper.vm.messages.length - 1];
    expect(lastMessage.role).toBe('assistant');
    expect(lastMessage.content).toContain('抱歉');
  });
});
