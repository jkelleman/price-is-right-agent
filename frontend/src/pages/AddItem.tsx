import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createItem } from '../api';
import { ItemCreate } from '../types';
import { Loader2 } from 'lucide-react';

export default function AddItem() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<ItemCreate>({
    name: '',
    url: '',
    current_price: undefined,
    target_price: undefined,
    image_url: '',
    description: '',
  });

  const createMutation = useMutation({
    mutationFn: createItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
      navigate('/');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === '' ? undefined : 
              (name.includes('price') ? parseFloat(value) : value),
    }));
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Add Item to Track
      </h1>

      <form onSubmit={handleSubmit} className="card space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Product Name *
          </label>
          <input
            type="text"
            name="name"
            required
            value={formData.name}
            onChange={handleChange}
            className="input"
            placeholder="e.g., Sony WH-1000XM5 Headphones"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Product URL *
          </label>
          <input
            type="url"
            name="url"
            required
            value={formData.url}
            onChange={handleChange}
            className="input"
            placeholder="https://www.amazon.com/..."
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Current Price
            </label>
            <input
              type="number"
              name="current_price"
              step="0.01"
              min="0"
              value={formData.current_price || ''}
              onChange={handleChange}
              className="input"
              placeholder="299.99"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Price
            </label>
            <input
              type="number"
              name="target_price"
              step="0.01"
              min="0"
              value={formData.target_price || ''}
              onChange={handleChange}
              className="input"
              placeholder="249.99"
            />
            <p className="text-xs text-gray-500 mt-1">
              Get alerted when price drops below this
            </p>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Image URL (optional)
          </label>
          <input
            type="url"
            name="image_url"
            value={formData.image_url}
            onChange={handleChange}
            className="input"
            placeholder="https://..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description (optional)
          </label>
          <textarea
            name="description"
            rows={3}
            value={formData.description}
            onChange={handleChange}
            className="input"
            placeholder="Additional notes about this product..."
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="flex-1 btn-primary flex items-center justify-center space-x-2"
          >
            {createMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                <span>Adding...</span>
              </>
            ) : (
              <span>Add Item</span>
            )}
          </button>

          <button
            type="button"
            onClick={() => navigate('/')}
            className="btn-secondary"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
