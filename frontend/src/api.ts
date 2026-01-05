import axios from 'axios';
import { Item, ItemCreate, PriceHistory, Alert, SimilarItem, BetterDeal } from './types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Items
export const getItems = async (): Promise<Item[]> => {
  const { data } = await api.get('/items');
  return data;
};

export const getItem = async (id: number): Promise<Item> => {
  const { data } = await api.get(`/items/${id}`);
  return data;
};

export const createItem = async (item: ItemCreate): Promise<Item> => {
  const { data } = await api.post('/items', item);
  return data;
};

export const deleteItem = async (id: number): Promise<void> => {
  await api.delete(`/items/${id}`);
};

// Price History
export const getPriceHistory = async (itemId: number): Promise<PriceHistory[]> => {
  const { data } = await api.get(`/items/${itemId}/history`);
  return data;
};

// Alerts
export const getAlerts = async (unreadOnly: boolean = false): Promise<Alert[]> => {
  const { data } = await api.get('/alerts', { params: { unread_only: unreadOnly } });
  return data;
};

export const markAlertRead = async (id: number): Promise<void> => {
  await api.patch(`/alerts/${id}/read`);
};

export const markAllAlertsRead = async (): Promise<void> => {
  await api.patch('/alerts/read-all');
};

export const deleteAlert = async (id: number): Promise<void> => {
  await api.delete(`/alerts/${id}`);
};

// AI/Similarity
export const getSimilarItems = async (itemId: number): Promise<SimilarItem[]> => {
  const { data } = await api.get(`/items/${itemId}/similar`);
  return data;
};

export const getBetterDeals = async (itemId: number): Promise<BetterDeal[]> => {
  const { data } = await api.get(`/items/${itemId}/better-deals`);
  return data;
};

export const findAlternatives = async (itemId: number): Promise<void> => {
  await api.post(`/items/${itemId}/find-alternatives`);
};
