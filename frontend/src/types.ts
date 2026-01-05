// API Types matching backend schemas

export interface Item {
  id: number;
  name: string;
  url: string;
  current_price: number | null;
  target_price: number | null;
  image_url: string | null;
  description: string | null;
  created_at: string;
  updated_at: string | null;
  is_active: boolean;
}

export interface ItemCreate {
  name: string;
  url: string;
  current_price?: number;
  target_price?: number;
  image_url?: string;
  description?: string;
}

export interface PriceHistory {
  id: number;
  item_id: number;
  price: number;
  recorded_at: string;
}

export interface Alert {
  id: number;
  item_id: number;
  alert_type: 'price_drop' | 'similar_item';
  message: string;
  sent_at: string;
  is_read: boolean;
}

export interface SimilarItem {
  item: Item;
  similarity_score: number;
}

export interface BetterDeal {
  item: Item;
  similarity_score: number;
  savings: number;
  savings_percent: number;
}
