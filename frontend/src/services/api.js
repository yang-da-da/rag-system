import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加请求时间戳
    config.metadata = { startTime: new Date() };
    
    // 添加用户代理信息
    config.headers['User-Agent'] = 'Financial-RAG-Frontend/1.0.0';
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = new Date();
    const startTime = response.config.metadata?.startTime;
    const duration = startTime ? endTime - startTime : 0;
    
    // 记录API调用日志
    console.log(`API Call: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status} (${duration}ms)`);
    
    return response;
  },
  (error) => {
    // 错误处理
    const errorMessage = error.response?.data?.detail || error.message || '未知错误';
    console.error(`API Error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${errorMessage}`);
    
    return Promise.reject(error);
  }
);

// API服务类
class FinancialRAGService {
  // 健康检查
  async healthCheck() {
    const response = await api.get('/api/health');
    return response.data;
  }

  // 金融术语标准化
  async standardizeText(text, options = {}) {
    const payload = {
      text,
      options: options.options || {},
      termTypes: options.termTypes || {},
      embeddingOptions: {
        provider: options.provider || 'huggingface',
        model: options.model || 'BAAI/bge-m3',
        dbName: options.dbName || 'financial_bge_m3',
        collectionName: options.collectionName || 'financial_concepts',
      },
      llmOptions: {
        provider: options.llmProvider || 'ollama',
        model: options.llmModel || 'qwen2.5:7b',
      },
    };

    const response = await api.post('/api/standardize', payload);
    return response.data;
  }

  // 金融实体识别
  async extractEntities(text, options = {}) {
    const payload = {
      text,
      options: options.options || {},
      termTypes: options.termTypes || {},
      embeddingOptions: {
        provider: options.provider || 'huggingface',
        model: options.model || 'BAAI/bge-m3',
        dbName: options.dbName || 'financial_bge_m3',
        collectionName: options.collectionName || 'financial_concepts',
      },
      llmOptions: {
        provider: options.llmProvider || 'ollama',
        model: options.llmModel || 'qwen2.5:7b',
      },
    };

    const response = await api.post('/api/ner', payload);
    return response.data;
  }

  // 金融缩写扩展
  async expandAbbreviation(text, context = '', method = 'simple_ollama', options = {}) {
    const payload = {
      text,
      context,
      method,
      embeddingOptions: {
        provider: options.provider || 'huggingface',
        model: options.model || 'BAAI/bge-m3',
        dbName: options.dbName || 'financial_bge_m3',
        collectionName: options.collectionName || 'financial_concepts',
      },
      llmOptions: {
        provider: options.llmProvider || 'ollama',
        model: options.llmModel || 'qwen2.5:7b',
      },
    };

    const response = await api.post('/api/abbreviation', payload);
    return response.data;
  }

  // 金融拼写纠正
  async correctText(text, options = {}) {
    const payload = {
      text,
      options: options.options || {},
      termTypes: options.termTypes || {},
      embeddingOptions: {
        provider: options.provider || 'huggingface',
        model: options.model || 'BAAI/bge-m3',
        dbName: options.dbName || 'financial_bge_m3',
        collectionName: options.collectionName || 'financial_concepts',
      },
      llmOptions: {
        provider: options.llmProvider || 'ollama',
        model: options.llmModel || 'qwen2.5:7b',
      },
    };

    const response = await api.post('/api/correction', payload);
    return response.data;
  }

  // 金融文本生成
  async generateText(prompt, options = {}) {
    const payload = {
      prompt,
      maxLength: options.maxLength || 500,
      temperature: options.temperature || 0.7,
      style: options.style || 'formal',
      llmOptions: {
        provider: options.llmProvider || 'ollama',
        model: options.llmModel || 'qwen2.5:7b',
      },
    };

    const response = await api.post('/api/generation', payload);
    return response.data;
  }
}

// 导出服务实例
export const financialRAGService = new FinancialRAGService();
export default api;
