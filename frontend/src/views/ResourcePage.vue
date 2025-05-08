<!-- filepath: e:\1_work\PersonalProgram\PsyChat\0421PsyChat\frontend\src\views\ResourcePage.vue -->
<!-- This component displays mental health resources with filtering options -->
<template>
  <!-- Main container with CSS class 'resources-container' -->
  <div class="resources-container">
    <!-- Page title -->
    <h2 class="page-title">心理健康资源</h2>
    
    <!-- Card containing filtering options -->
    <el-card class="filter-card">
      <!-- Form for filter controls with inline layout -->
      <el-form :inline="true" :model="filterForm" class="filter-form">
        <!-- Form item for category filter -->
        <el-form-item label="分类">
          <!-- Dropdown select for categories -->
          <el-select v-model="filterForm.category" placeholder="选择分类" clearable>
            <!-- Generate an option for each category in the categories array -->
            <el-option 
              v-for="category in categories" 
              :key="category.value" 
              :label="category.label" 
              :value="category.value" 
            />
          </el-select>
        </el-form-item>
        
        <!-- Form item for location filter -->
        <el-form-item label="地区">
          <!-- Dropdown select for locations -->
          <el-select v-model="filterForm.location" placeholder="选择地区" clearable>
            <!-- Generate an option for each location in the locations array -->
            <el-option 
              v-for="location in locations" 
              :key="location.value" 
              :label="location.label" 
              :value="location.value" 
            />
          </el-select>
        </el-form-item>
        
        <!-- Form item for filter action buttons -->
        <el-form-item>
          <!-- Button to apply filters -->
          <el-button type="primary" @click="fetchResources">筛选</el-button>
          <!-- Button to reset filters -->
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- Card containing the resources list with loading state -->
    <el-card v-loading="loading" class="resources-card">
      <!-- Show resources list if there are resources -->
      <template v-if="resources.length">
        <!-- Grid container for resources -->
        <div class="resources-list">
          <!-- Generate a card for each resource -->
          <el-card 
            v-for="resource in resources" 
            :key="resource.id" 
            class="resource-item"
          >
            <!-- Resource title -->
            <h3>{{ resource.title }}</h3>
            <!-- Resource description -->
            <p class="resource-description">{{ resource.description }}</p>
            
            <!-- Resource metadata tags (category and location) -->
            <div class="resource-meta">
              <!-- Category tag -->
              <el-tag size="small">{{ resource.category }}</el-tag>
              <!-- Location tag (if present) -->
              <el-tag size="small" type="info" v-if="resource.location_tag">
                {{ resource.location_tag }}
              </el-tag>
            </div>
            
            <!-- Contact information (if present) -->
            <div class="resource-contact" v-if="resource.contact_info">
              <strong>联系方式:</strong> {{ resource.contact_info }}
            </div>
            
            <!-- Link to resource (if present) -->
            <div class="resource-link" v-if="resource.url">
              <!-- Button to open the resource URL -->
              <el-button type="primary" size="small" @click="openLink(resource.url)">
                访问资源
              </el-button>
            </div>
          </el-card>
        </div>
      </template>
      
      <!-- Show empty state when no resources match filters -->
      <el-empty v-else description="暂无符合条件的资源" />
    </el-card>
  </div>
</template>

<script>
// Import necessary functions from Vue
import { ref, reactive, onMounted } from 'vue';
// Import API service for data fetching
import api from '../services/api';
// Import Element Plus message component for notifications
import { ElMessage } from 'element-plus';

// Define and export the component
export default {
  // Setup function defines component logic and returns data to the template
  setup() {
    // Reactive array to store fetched resources
    const resources = ref([]);
    // Boolean to track loading state
    const loading = ref(false);
    
    // Reactive object to store filter values
    const filterForm = reactive({
      category: '',  // Selected category filter
      location: ''   // Selected location filter
    });
    
    // Array of category options for the filter dropdown
    // Note: This could be fetched from the API in a real application
    const categories = [
      { label: '咨询服务', value: 'counseling' },
      { label: '危机干预', value: 'crisis' },
      { label: '支持团体', value: 'support' },
      { label: '教育资源', value: 'education' }
    ];
    
    // Array of location options for the filter dropdown
    // Note: This could be fetched from the API in a real application
    const locations = [
      { label: '全国', value: 'national' },
      { label: '北京', value: 'beijing' },
      { label: '上海', value: 'shanghai' },
      { label: '广州', value: 'guangzhou' },
      { label: '线上', value: 'online' }
    ];
    
    // Function to fetch resources from the API
    const fetchResources = async () => {
      // Set loading state to true
      loading.value = true;
      try {
        // Call API with current filter values
        const response = await api.getResources({
          category: filterForm.category,
          location: filterForm.location,
        });
        // Store the fetched resources in the reactive variable
        resources.value = response.data;
      } catch (error) {
        // Log error to console for debugging
        console.error('Error fetching resources:', error);
        // Show error message to user
        ElMessage.error('获取资源失败，请稍后再试');
      } finally {
        // Set loading state to false regardless of success or failure
        loading.value = false;
      }
    };
    
    // Function to reset all filters and fetch resources again
    const resetFilters = () => {
      // Clear both filter values
      filterForm.category = '';
      filterForm.location = '';
      // Fetch resources with cleared filters
      fetchResources();
    };
    
    // Function to open resource URL in a new tab
    const openLink = (url) => {
      window.open(url, '_blank');
    };
    
    // Fetch resources when component is mounted
    onMounted(() => {
      fetchResources();
    });
    
    // Return data and functions to make them available in the template
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
/* Container for the resources page */
.resources-container {
  max-width: 1000px;  /* Limit width for better readability */
  margin: 0 auto;     /* Center the container horizontally */
}

/* Styling for the page title */
.page-title {
  text-align: center;    /* Center the title text */
  margin-bottom: 20px;   /* Add space below the title */
  color: #303133;        /* Dark gray color for text */
}

/* Styling for the filter card */
.filter-card {
  margin-bottom: 20px;   /* Add space below the filter card */
}

/* Styling for the filter form */
.filter-form {
  display: flex;          /* Use flexbox for layout */
  flex-wrap: wrap;        /* Allow items to wrap on small screens */
  justify-content: center; /* Center form items */
}

/* Grid layout for the resources list */
.resources-list {
  display: grid;          /* Use CSS grid for layout */
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); /* Responsive grid columns */
  gap: 20px;              /* Space between grid items */
}

/* Styling for individual resource cards */
.resource-item {
  height: 100%;          /* Take full height of grid cell */
  display: flex;          /* Use flexbox for layout */
  flex-direction: column; /* Stack content vertically */
}

/* Styling for resource descriptions */
.resource-description {
  flex-grow: 1;          /* Allow description to take available space */
  color: #606266;        /* Medium gray color for text */
  margin-bottom: 15px;   /* Add space below description */
}

/* Styling for metadata tags container */
.resource-meta {
  display: flex;         /* Use flexbox for layout */
  gap: 10px;             /* Space between tags */
  margin: 10px 0;        /* Vertical margin */
}

/* Styling for contact information */
.resource-contact {
  margin: 10px 0;        /* Vertical margin */
  font-size: 14px;       /* Smaller text size */
  color: #606266;        /* Medium gray color for text */
}

/* Styling for link button container */
.resource-link {
  margin-top: 10px;      /* Space above the button */
}
</style>