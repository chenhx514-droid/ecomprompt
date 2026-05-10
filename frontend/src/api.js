import axios from 'axios';

const api = axios.create({ baseURL: '/api' });

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
