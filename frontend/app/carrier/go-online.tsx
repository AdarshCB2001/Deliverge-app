import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function GoOnlineScreen() {
  const router = useRouter();
  const [isOnline, setIsOnline] = useState(false);

  const handleToggleOnline = () => {
    if (!isOnline) {
      Alert.alert(
        'Go Online',
        'You will start receiving delivery requests along your route.',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Go Online',
            onPress: () => {
              setIsOnline(true);
              Alert.alert('Success', 'You are now online and can accept deliveries!');
            },
          },
        ]
      );
    } else {
      setIsOnline(false);
      Alert.alert('Offline', 'You will no longer receive delivery requests');
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Carrier Mode</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={[styles.statusCard, isOnline ? styles.statusCardOnline : styles.statusCardOffline]}>
          <Ionicons
            name={isOnline ? 'checkmark-circle' : 'close-circle'}
            size={64}
            color={isOnline ? '#4CAF50' : '#999'}
          />
          <Text style={styles.statusText}>{isOnline ? 'You are Online' : 'You are Offline'}</Text>
          <Text style={styles.statusSubtext}>
            {isOnline
              ? 'Nearby delivery requests will appear here'
              : 'Go online to start receiving delivery requests'}
          </Text>
        </View>

        <TouchableOpacity
          style={[styles.toggleButton, isOnline ? styles.toggleButtonOnline : styles.toggleButtonOffline]}
          onPress={handleToggleOnline}
        >
          <Text style={styles.toggleButtonText}>{isOnline ? 'Go Offline' : 'Go Online'}</Text>
        </TouchableOpacity>

        {isOnline && (
          <View style={styles.earningsCard}>
            <Text style={styles.earningsTitle}>Today's Earnings</Text>
            <Text style={styles.earningsAmount}>\u20b90</Text>
            <Text style={styles.earningsSubtext}>0 deliveries completed</Text>
          </View>
        )}

        <View style={styles.infoSection}>
          <Text style={styles.infoTitle}>How it Works</Text>
          
          <View style={styles.infoItem}>
            <View style={styles.infoIcon}>
              <Text style={styles.infoNumber}>1</Text>
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoItemTitle}>Set Your Destination</Text>
              <Text style={styles.infoItemText}>Tell us where you're going</Text>
            </View>
          </View>

          <View style={styles.infoItem}>
            <View style={styles.infoIcon}>
              <Text style={styles.infoNumber}>2</Text>
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoItemTitle}>See Delivery Requests</Text>
              <Text style={styles.infoItemText}>Get requests along your route</Text>
            </View>
          </View>

          <View style={styles.infoItem}>
            <View style={styles.infoIcon}>
              <Text style={styles.infoNumber}>3</Text>
            </View>
            <View style={styles.infoContent}>
              <Text style={styles.infoItemTitle}>Accept & Deliver</Text>
              <Text style={styles.infoItemText}>Pick up, deliver, earn cash</Text>
            </View>
          </View>
        </View>

        <View style={styles.noteCard}>
          <Ionicons name="information-circle" size={20} color="#2196F3" />
          <Text style={styles.noteText}>
            Note: Full carrier mode with live GPS tracking, delivery requests, and earnings tracking coming in Phase 2
          </Text>
        </View>
      </ScrollView>
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
  content: {
    padding: 16,
  },
  statusCard: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
  },
  statusCardOnline: {
    borderWidth: 2,
    borderColor: '#4CAF50',
  },
  statusCardOffline: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  statusText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 16,
  },
  statusSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginTop: 8,
  },
  toggleButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 24,
  },
  toggleButtonOnline: {
    backgroundColor: '#FF5252',
  },
  toggleButtonOffline: {
    backgroundColor: '#4CAF50',
  },
  toggleButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  earningsCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24,
  },
  earningsTitle: {
    fontSize: 14,
    color: '#2E7D32',
    marginBottom: 8,
  },
  earningsAmount: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1B5E20',
    marginBottom: 4,
  },
  earningsSubtext: {
    fontSize: 12,
    color: '#4CAF50',
  },
  infoSection: {
    marginBottom: 16,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  infoItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  infoIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#E05A3A',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  infoNumber: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
  },
  infoContent: {
    flex: 1,
  },
  infoItemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  infoItemText: {
    fontSize: 14,
    color: '#666',
  },
  noteCard: {
    flexDirection: 'row',
    backgroundColor: '#E3F2FD',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  noteText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 13,
    color: '#1976D2',
    lineHeight: 18,
  },
});
