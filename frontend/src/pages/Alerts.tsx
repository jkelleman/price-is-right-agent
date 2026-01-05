import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAlerts, markAlertRead, markAllAlertsRead, deleteAlert } from '../api';
import { Bell, Check, Trash2, TrendingDown, Sparkles, Loader2 } from 'lucide-react';
import { format } from 'date-fns';
import { Alert as AlertType } from '../types';

export default function Alerts() {
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => getAlerts(false),
  });

  const markReadMutation = useMutation({
    mutationFn: markAlertRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: markAllAlertsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAlert,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  const unreadAlerts = alerts?.filter(a => !a.is_read) || [];

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Alerts
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {unreadAlerts.length} unread notification{unreadAlerts.length !== 1 ? 's' : ''}
          </p>
        </div>

        {unreadAlerts.length > 0 && (
          <button
            onClick={() => markAllReadMutation.mutate()}
            disabled={markAllReadMutation.isPending}
            className="btn-primary flex items-center space-x-2"
          >
            <Check className="w-5 h-5" />
            <span>Mark All Read</span>
          </button>
        )}
      </div>

      {!alerts || alerts.length === 0 ? (
        <div className="card text-center py-12">
          <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500 dark:text-gray-400">
            No alerts yet. We'll notify you when prices drop!
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {alerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onMarkRead={() => markReadMutation.mutate(alert.id)}
              onDelete={() => deleteMutation.mutate(alert.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface AlertCardProps {
  alert: AlertType;
  onMarkRead: () => void;
  onDelete: () => void;
}

function AlertCard({ alert, onMarkRead, onDelete }: AlertCardProps) {
  const Icon = alert.alert_type === 'price_drop' ? TrendingDown : Sparkles;
  const bgColor = alert.alert_type === 'price_drop' 
    ? 'bg-green-50 dark:bg-green-900/20'
    : 'bg-blue-50 dark:bg-blue-900/20';
  const iconColor = alert.alert_type === 'price_drop'
    ? 'text-green-600 dark:text-green-400'
    : 'text-blue-600 dark:text-blue-400';

  return (
    <div
      className={`card ${!alert.is_read ? 'border-l-4 border-primary-500' : ''} ${
        alert.is_read ? 'opacity-60' : ''
      }`}
    >
      <div className="flex items-start space-x-4">
        <div className={`p-3 rounded-lg ${bgColor}`}>
          <Icon className={`w-6 h-6 ${iconColor}`} />
        </div>

        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {alert.alert_type === 'price_drop' ? 'Price Drop Alert' : 'Similar Item Found'}
            </h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">
              {format(new Date(alert.sent_at), 'MMM dd, yyyy h:mm a')}
            </span>
          </div>

          <p className="text-gray-600 dark:text-gray-300 mb-4">
            {alert.message}
          </p>

          <div className="flex space-x-2">
            {!alert.is_read && (
              <button
                onClick={onMarkRead}
                className="btn-secondary text-sm flex items-center space-x-1"
              >
                <Check className="w-4 h-4" />
                <span>Mark Read</span>
              </button>
            )}

            <button
              onClick={onDelete}
              className="text-red-600 hover:text-red-700 text-sm flex items-center space-x-1"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
