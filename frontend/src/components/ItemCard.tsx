import { Link } from 'react-router-dom';
import { TrendingDown, TrendingUp, ExternalLink } from 'lucide-react';
import { Item } from '../types';

interface ItemCardProps {
  item: Item;
  onDelete?: (id: number) => void;
}

export default function ItemCard({ item, onDelete }: ItemCardProps) {
  const isPriceBelowTarget = 
    item.current_price && item.target_price && item.current_price <= item.target_price;

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <Link to={`/items/${item.id}`} className="block">
        {item.image_url && (
          <img
            src={item.image_url}
            alt={item.name}
            className="w-full h-48 object-cover rounded-t-lg -m-6 mb-4"
          />
        )}
        
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {item.name}
        </h3>
        
        {item.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
            {item.description}
          </p>
        )}

        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-gray-500 dark:text-gray-400">Current Price</p>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">
              {item.current_price ? `$${item.current_price.toFixed(2)}` : 'N/A'}
            </p>
          </div>
          
          {item.target_price && (
            <div className="text-right">
              <p className="text-sm text-gray-500 dark:text-gray-400">Target</p>
              <p className="text-lg font-medium text-gray-700 dark:text-gray-300">
                ${item.target_price.toFixed(2)}
              </p>
            </div>
          )}
        </div>

        {isPriceBelowTarget && (
          <div className="bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-4 py-2 rounded-lg flex items-center space-x-2 mb-4">
            <TrendingDown className="w-5 h-5" />
            <span className="font-medium">Below target price!</span>
          </div>
        )}
      </Link>

      <div className="flex space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 btn-primary flex items-center justify-center space-x-2"
          onClick={(e) => e.stopPropagation()}
        >
          <ExternalLink className="w-4 h-4" />
          <span>View Product</span>
        </a>
        
        {onDelete && (
          <button
            onClick={(e) => {
              e.preventDefault();
              onDelete(item.id);
            }}
            className="btn-secondary"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
