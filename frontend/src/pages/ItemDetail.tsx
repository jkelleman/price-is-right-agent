import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getItem, getPriceHistory, getSimilarItems } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { ArrowLeft, ExternalLink, Loader2, Sparkles } from 'lucide-react';
import { format } from 'date-fns';

export default function ItemDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const itemId = parseInt(id || '0');

  const { data: item, isLoading: itemLoading } = useQuery({
    queryKey: ['items', itemId],
    queryFn: () => getItem(itemId),
    enabled: !!itemId,
  });

  const { data: priceHistory } = useQuery({
    queryKey: ['priceHistory', itemId],
    queryFn: () => getPriceHistory(itemId),
    enabled: !!itemId,
  });

  const { data: similarItems } = useQuery({
    queryKey: ['similarItems', itemId],
    queryFn: () => getSimilarItems(itemId),
    enabled: !!itemId,
  });

  if (itemLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (!item) {
    return <div>Item not found</div>;
  }

  const chartData = priceHistory?.map(h => ({
    date: format(new Date(h.recorded_at), 'MMM dd'),
    price: h.price,
  })) || [];

  return (
    <div>
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6"
      >
        <ArrowLeft className="w-5 h-5" />
        <span>Back to Dashboard</span>
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Item Details */}
        <div className="card">
          {item.image_url && (
            <img
              src={item.image_url}
              alt={item.name}
              className="w-full h-64 object-cover rounded-lg mb-6"
            />
          )}

          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            {item.name}
          </h1>

          {item.description && (
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {item.description}
            </p>
          )}

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Current Price</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {item.current_price ? `$${item.current_price.toFixed(2)}` : 'N/A'}
              </p>
            </div>

            {item.target_price && (
              <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">Target Price</p>
                <p className="text-3xl font-bold text-gray-900 dark:text-white">
                  ${item.target_price.toFixed(2)}
                </p>
              </div>
            )}
          </div>

          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <ExternalLink className="w-5 h-5" />
            <span>View on Store</span>
          </a>
        </div>

        {/* Price History Chart */}
        <div className="card">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Price History
          </h2>

          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500 dark:text-gray-400 text-center py-12">
              No price history available yet
            </p>
          )}
        </div>
      </div>

      {/* Similar Items */}
      {similarItems && similarItems.length > 0 && (
        <div className="mt-8">
          <div className="flex items-center space-x-2 mb-6">
            <Sparkles className="w-6 h-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Similar Items You Might Like
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {similarItems.map(({ item: similarItem, similarity_score }) => (
              <div key={similarItem.id} className="card">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-primary-600">
                    {(similarity_score * 100).toFixed(0)}% match
                  </span>
                </div>
                
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
                  {similarItem.name}
                </h3>
                
                <p className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  {similarItem.current_price ? `$${similarItem.current_price.toFixed(2)}` : 'N/A'}
                </p>

                <button
                  onClick={() => navigate(`/items/${similarItem.id}`)}
                  className="btn-primary w-full"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
