import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';
import api from '../../utils/api';

interface Transaction {
  delivery_id: string;
  amount: number;
  type: 'earned' | 'paid';
  status: 'completed' | 'pending';
  created_at: string;
}

export default function PaymentHistoryScreen() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalEarned, setTotalEarned] = useState(0);
  const [totalPaid, setTotalPaid] = useState(0);

  useEffect(() => {
    fetchPaymentHistory();
  }, []);

  const fetchPaymentHistory = async () => {
    try {
      // Fetch completed deliveries
      const response = await api.get('/deliveries', {
        params: { status: 'delivered' },
      });

      const deliveries = response.data || [];
      const txns: Transaction[] = [];
      let earned = 0;
      let paid = 0;

      deliveries.forEach((delivery: any) => {
        const isCarrier = delivery.carrier_id === user?.user_id;
        const isSender = delivery.sender_id === user?.user_id;

        if (isCarrier) {
          txns.push({
            delivery_id: delivery.delivery_id,
            amount: delivery.price_rs,
            type: 'earned',
            status: 'completed',
            created_at: delivery.delivered_at,
          });
          earned += delivery.price_rs;
        } else if (isSender) {
          txns.push({
            delivery_id: delivery.delivery_id,
            amount: delivery.price_rs,
            type: 'paid',
            status: 'completed',
            created_at: delivery.delivered_at,
          });
          paid += delivery.price_rs;
        }
      });

      setTransactions(txns.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
      setTotalEarned(earned);
      setTotalPaid(paid);
    } catch (error) {
      console.error('Error fetching payment history:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Payment History</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#E05A3A" />
        </View>
      ) : (
        <ScrollView style={styles.content}>
          {/* Summary Cards */}
          <View style={styles.summaryContainer}>
            <View style={[styles.summaryCard, { backgroundColor: '#E8F5E9' }]}>
              <Ionicons name="arrow-down-circle" size={32} color="#4CAF50" />
              <Text style={styles.summaryAmount}>₹{totalEarned}</Text>
              <Text style={styles.summaryLabel}>Total Earned</Text>
            </View>

            <View style={[styles.summaryCard, { backgroundColor: '#FFF3E0' }]}>
              <Ionicons name="arrow-up-circle" size={32} color="#FF9800" />
              <Text style={styles.summaryAmount}>₹{totalPaid}</Text>
              <Text style={styles.summaryLabel}>Total Paid</Text>
            </View>
          </View>

          {/* Payment Notice */}
          <View style={styles.noticeCard}>
            <Ionicons name="information-circle" size={24} color="#2196F3" />
            <Text style={styles.noticeText}>
              All transactions are cash-based. Payment is collected/paid at delivery.
            </Text>
          </View>

          {/* Transactions List */}
          <Text style={styles.sectionTitle}>Transaction History</Text>

          {transactions.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="wallet-outline" size={64} color="#ccc" />
              <Text style={styles.emptyText}>No transactions yet</Text>
              <Text style={styles.emptySubtext}>
                Your payment history will appear here
              </Text>
            </View>
          ) : (
            transactions.map((txn) => (
              <View key={txn.delivery_id} style={styles.transactionCard}>
                <View style={styles.transactionIcon}>
                  <Ionicons
                    name={txn.type === 'earned' ? 'arrow-down' : 'arrow-up'}
                    size={20}
                    color={txn.type === 'earned' ? '#4CAF50' : '#FF9800'}
                  />
                </View>

                <View style={styles.transactionDetails}>
                  <Text style={styles.transactionType}>
                    {txn.type === 'earned' ? 'Earned from delivery' : 'Paid for delivery'}
                  </Text>
                  <Text style={styles.transactionId}>
                    #{txn.delivery_id.slice(9)}
                  </Text>
                  <Text style={styles.transactionDate}>
                    {new Date(txn.created_at).toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'short',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </Text>
                </View>

                <View style={styles.transactionAmount}>
                  <Text
                    style={[
                      styles.amountText,
                      { color: txn.type === 'earned' ? '#4CAF50' : '#FF9800' },
                    ]}
                  >
                    {txn.type === 'earned' ? '+' : '-'}₹{txn.amount}
                  </Text>
                  <View style={styles.statusBadge}>
                    <Text style={styles.statusText}>CASH</Text>
                  </View>
                </View>
              </View>
            ))
          )}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9F9F9',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  summaryContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  summaryCard: {
    flex: 1,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  summaryAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  noticeCard: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FD',
    marginHorizontal: 16,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 16,
  },
  noticeText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 13,
    color: '#1976D2',
    lineHeight: 18,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginHorizontal: 16,
    marginBottom: 12,
  },
  transactionCard: {
    flexDirection: 'row',
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    alignItems: 'center',
  },
  transactionIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  transactionDetails: {
    flex: 1,
  },
  transactionType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  transactionId: {
    fontSize: 12,
    color: '#E05A3A',
    marginBottom: 2,
  },
  transactionDate: {
    fontSize: 11,
    color: '#999',
  },
  transactionAmount: {
    alignItems: 'flex-end',
  },
  amountText: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statusBadge: {
    backgroundColor: '#f5f5f5',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 4,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#666',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64,
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
  },
  emptySubtext: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
  },
});