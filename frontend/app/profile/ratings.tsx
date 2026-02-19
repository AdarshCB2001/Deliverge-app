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
import api from '../../utils/api';

interface Rating {
  rating_id: string;
  delivery_id: string;
  rater_id: string;
  ratee_id: string;
  stars: number;
  review_text?: string;
  created_at: string;
}

export default function MyRatingsScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [ratings, setRatings] = useState<Rating[]>([]);
  const [averageRating, setAverageRating] = useState(0);

  useEffect(() => {
    fetchRatings();
  }, []);

  const fetchRatings = async () => {
    try {
      // We'll need to add this endpoint
      const response = await api.get('/ratings/me');
      setRatings(response.data.ratings || []);
      setAverageRating(response.data.average_rating || 0);
    } catch (error) {
      console.error('Error fetching ratings:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (stars: number) => {
    return (
      <View style={styles.starsContainer}>
        {[1, 2, 3, 4, 5].map((star) => (
          <Ionicons
            key={star}
            name={star <= stars ? 'star' : 'star-outline'}
            size={16}
            color="#FFB800"
          />
        ))}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>My Ratings</Text>
        <View style={{ width: 40 }} />
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#E05A3A" />
        </View>
      ) : (
        <ScrollView style={styles.content}>
          {/* Average Rating Card */}
          <View style={styles.averageCard}>
            <Text style={styles.averageRating}>{averageRating.toFixed(1)}</Text>
            {renderStars(Math.round(averageRating))}
            <Text style={styles.ratingCount}>{ratings.length} ratings</Text>
          </View>

          {/* Ratings List */}
          {ratings.length === 0 ? (
            <View style={styles.emptyContainer}>
              <Ionicons name="star-outline" size={64} color="#ccc" />
              <Text style={styles.emptyText}>No ratings yet</Text>
              <Text style={styles.emptySubtext}>
                Complete deliveries to receive ratings
              </Text>
            </View>
          ) : (
            ratings.map((rating) => (
              <View key={rating.rating_id} style={styles.ratingCard}>
                <View style={styles.ratingHeader}>
                  {renderStars(rating.stars)}
                  <Text style={styles.ratingDate}>
                    {new Date(rating.created_at).toLocaleDateString()}
                  </Text>
                </View>
                {rating.review_text && (
                  <Text style={styles.reviewText}>{rating.review_text}</Text>
                )}
                <Text style={styles.deliveryId}>Delivery #{rating.delivery_id.slice(9)}</Text>
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
  averageCard: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 24,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  averageRating: {
    fontSize: 48,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  starsContainer: {
    flexDirection: 'row',
    gap: 4,
    marginBottom: 8,
  },
  ratingCount: {
    fontSize: 14,
    color: '#666',
  },
  ratingCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 12,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  ratingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  ratingDate: {
    fontSize: 12,
    color: '#999',
  },
  reviewText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
    marginBottom: 8,
  },
  deliveryId: {
    fontSize: 12,
    color: '#E05A3A',
    fontWeight: '600',
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