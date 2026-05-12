import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const token = localStorage.getItem('access_token');
      if (token) {
        localStorage.removeItem('access_token');
        window.dispatchEvent(new Event('auth:logout'));
      }
    }
    return Promise.reject(error);
  }
);

export async function fetchPrompts(params = {}) {
  const { data } = await api.get('/prompts', { params });
  return data;
}

export async function fetchPrompt(id) {
  const { data } = await api.get(`/prompts/${id}`);
  return data;
}

export async function usePrompt(id) {
  await api.post(`/prompts/${id}/use`);
}

export async function generatePrompt(params) {
  const { data } = await api.post('/generate', params);
  return data;
}

export async function enhancePrompt(id) {
  const { data } = await api.post(`/enhance/${id}`);
  return data;
}

export async function fetchHotCategories() {
  const { data } = await api.get('/trends/hot-categories');
  return data;
}

export async function fetchHotKeywords() {
  const { data } = await api.get('/trends/keywords');
  return data;
}

export async function fetchTrendCalendar() {
  const { data } = await api.get('/trends/calendar');
  return data;
}

export async function importFile(file) {
  const form = new FormData();
  form.append('file', file);
  const { data } = await api.post('/import', form);
  return data;
}

export async function fetchFolders() {
  const { data } = await api.get('/folders');
  return data.folders;
}

export async function collectPrompt({ title, category, scenario, platform, output_type, content, folder, images }) {
  const form = new FormData();
  form.append('title', title);
  form.append('category', category);
  form.append('scenario', scenario);
  form.append('platform', platform);
  form.append('output_type', output_type);
  form.append('content', content);
  form.append('folder', folder || '默认');
  for (const img of images) {
    form.append('images', img);
  }
  const { data } = await api.post('/collect', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

// --- 个人仓库 ---
export async function fetchLibraryStats() {
  const { data } = await api.get('/library/stats');
  return data;
}

export async function deleteLibraryPrompt(id) {
  const { data } = await api.delete(`/library/${id}`);
  return data;
}

export async function moveLibraryPrompt(id, folder) {
  const { data } = await api.put(`/library/${id}/folder`, null, { params: { folder } });
  return data;
}
