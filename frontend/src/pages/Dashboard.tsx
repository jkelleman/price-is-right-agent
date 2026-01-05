import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getItems, deleteItem } from '../api';
import ItemCard from '../components/ItemCard';
import { Loader2 } from 'lucide-react';

export default function Dashboard() {
  const queryClient = useQueryClient();
  
  const { data: items, isLoading } = useQuery({
    queryKey: ['items'],
    queryFn: getItems,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Your Tracked Items
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Monitor prices and get alerted when they drop
        </p>
      </div>

      {!items || items.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 dark:text-gray-400 mb-4">
            No items tracked yet. Start by adding an item!
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {items.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              onDelete={(id) => deleteMutation.mutate(id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
