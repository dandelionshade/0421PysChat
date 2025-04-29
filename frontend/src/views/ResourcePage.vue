<!-- filepath: e:\1_work\PersonalProgram\PsyChat\0421PsyChat\frontend\src\views\ResourcePage.vue -->
<template>
  <div class="resources-container">
    <h2 class="page-title">心理健康资源</h2>
    
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <el-form-item label="分类">
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <el-option 
              v-for="category in categories" 
              :key="category.value" 
              :label="category.label" 
              :value="category.value" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="地区">
          <el-select v-model="filterForm.location" placeholder="选择地区" clearable>
            <el-option 
              v-for="location in locations" 
              :key="location.value" 
              :label="location.label" 
              :value="location.value" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="fetchResources">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-loading="loading" class="resources-card">
      <template v-if="resources.length">
        <div class="resources-list">
          <el-card 
            v-for="resource in resources" 
            :key="resource.id" 
            class="resource-item"
          >
            <h3>{{ resource.title }}</h3>
            <p class="resource-description">{{ resource.description }}</p>
            
            <div class="resource-meta">
              <el-tag size="small">{{ resource.category }}</el-tag>
              <el-tag size="small" type="info" v-if="resource.location_tag">
                {{ resource.location_tag }}
              </el-tag>
            </div>
            
            <div class="resource-contact" v-if="resource.contact_info">
              <strong>联系方式:</strong> {{ resource.contact_info }}
            </div>
            
            <div class="resource-link" v-if="resource.url">
              <el-button type="primary" size="small" @click="openLink(resource.url)">
                访问资源
              </el-button>
            </div>
          </el-card>
        </div>
      </template>
      
      <el-empty v-else description="暂无符合条件的资源" />
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import api from '../services/api';
import { ElMessage } from 'element-plus';

export default {
  setup() {
    const resources = ref([]);
    const loading = ref(false);
    
    const filterForm = reactive({
      category: '',
      location: ''
    });
    
    // 这些分类和地区可以从后端获取，这里使用静态数据作为示例
    const categories = [
      { label: '咨询服务', value: 'counseling' },
      { label: '危机干预', value: 'crisis' },
      { label: '支持团体', value: 'support' },
      { label: '教育资源', value: 'education' }
    ];
    
    const locations = [
      { label: '全国', value: 'national' },
      { label: '北京', value: 'beijing' },
      { label: '上海', value: 'shanghai' },
      { label: '广州', value: 'guangzhou' },
      { label: '线上', value: 'online' }
    ];
    
    const fetchResources = async () => {
      loading.value = true;
      try {
        const response = await api.getResources({
          category: filterForm.category,
          location: filterForm.location,
        });
        resources.value = response.data;
      } catch (error) {
        console.error('Error fetching resources:', error);
        ElMessage.error('获取资源失败，请稍后再试');
      } finally {
        loading.value = false;
      }
    };
    
    const resetFilters = () => {
      filterForm.category = '';
      filterForm.location = '';
      fetchResources();
    };
    
    const openLink = (url) => {
      window.open(url, '_blank');
    };
    
    onMounted(() => {
      fetchResources();
    });
    
    return {
      resources,
      loading,
      filterForm,
      categories,
      locations,
      fetchResources,
      resetFilters,
      openLink,
    };
  }
}
</script>

<style scoped>
.resources-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-title {
  text-align: center;
  margin-bottom: 20px;
  color: #303133;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

.resources-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.resource-item {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.resource-description {
  flex-grow: 1;
  color: #606266;
  margin-bottom: 15px;
}

.resource-meta {
  display: flex;
  gap: 10px;
  margin: 10px 0;
}

.resource-contact {
  margin: 10px 0;
  font-size: 14px;
  color: #606266;
}

.resource-link {
  margin-top: 10px;
}
</style>