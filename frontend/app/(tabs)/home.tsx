import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Switch,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuthStore } from '../../store/authStore';
import api from '../../utils/api';

export default function HomeScreen() {
  const { user, setUser } = useAuthStore();
  const router = useRouter();
  const [switching, setSwitching] = React.useState(false);

  const isSender = user?.role === 'sender';
  const isCarrier = user?.role === 'carrier';

  const handleRoleSwitch = async () => {
    if (!user) return;
    
    setSwitching(true);
    try {
      const newRole = isSender ? 'carrier' : 'sender';
      await api.put('/users/role', null, {
        params: { role: newRole },
      });
      
      // Update local user
      setUser({ ...user, role: newRole });
    } catch (error) {
      console.error('Error switching role:', error);
    } finally {
      setSwitching(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>DELIVERGE</Text>
        <Text style={styles.greeting}>Hi, {user?.name?.split(' ')[0]}!</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        {/* Role Switcher */}
        <View style={styles.roleSwitcher}>
          <View style={styles.roleOption}>
            <View>
              <Text style={styles.roleTitle}>I want to send</Text>
              <Text style={styles.roleSubtitle}>Post a parcel for delivery</Text>
            </View>
            <View style={styles.switchContainer}>
              <Text style={[styles.roleLabel, isSender && styles.activeRole]}>Sender</Text>
              <Switch
                value={isCarrier}
                onValueChange={handleRoleSwitch}
                trackColor={{ false: '#E05A3A', true: '#4CAF50' }}
                thumbColor="#fff"
                disabled={switching}
              />
              <Text style={[styles.roleLabel, isCarrier && styles.activeRole]}>Carrier</Text>
            </View>
          </View>
          <View style={styles.dividerLine} />
          <View style={styles.roleOption}>
            <View>
              <Text style={styles.roleTitle}>I want to earn</Text>
              <Text style={styles.roleSubtitle}>Deliver parcels along my route</Text>
            </View>
          </View>
        </View>

        {/* Sender Actions */}
        {isSender && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Send a Parcel</Text>
            <TouchableOpacity 
              style={styles.primaryCard}
              onPress={() => router.push('/sender/post-parcel')}
            >
              <View style={styles.cardIcon}>
                <Ionicons name="cube-outline" size={32} color="#fff" />
              </View>
              <View style={styles.cardContent}>
                <Text style={styles.cardTitle}>Post New Delivery</Text>
                <Text style={styles.cardSubtitle}>Send a parcel anywhere in Goa</Text>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#fff" />
            </TouchableOpacity>

            <View style={styles.quickStats}>
              <View style={styles.statCard}>
                <Ionicons name="checkmark-circle" size={24} color="#4CAF50" />
                <Text style={styles.statNumber}>0</Text>
                <Text style={styles.statLabel}>Delivered</Text>
              </View>
              <View style={styles.statCard}>
                <Ionicons name="time" size={24} color="#FF9800" />
                <Text style={styles.statNumber}>0</Text>
                <Text style={styles.statLabel}>In Transit</Text>
              </View>
            </View>
          </View>
        )}

        {/* Carrier Actions */}
        {isCarrier && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Earn as Carrier</Text>
            <TouchableOpacity 
              style={styles.primaryCard}
              onPress={() => router.push('/carrier/go-online')}
            >
              <View style={styles.cardIcon}>
                <Ionicons name="car-outline" size={32} color="#fff" />
              </View>
              <View style={styles.cardContent}>
                <Text style={styles.cardTitle}>Go Online</Text>
                <Text style={styles.cardSubtitle}>Start accepting deliveries</Text>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#fff" />
            </TouchableOpacity>

            <TouchableOpacity 
              style={styles.secondaryCard}
              onPress={() => router.push('/carrier/kyc')}
            >
              <Ionicons name="shield-checkmark-outline" size={24} color="#E05A3A" />
              <View style={{ flex: 1, marginLeft: 12 }}>
                <Text style={styles.secondaryCardTitle}>Complete KYC</Text>
                <Text style={styles.secondaryCardSubtitle}>Verify to start earning</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#666" />
            </TouchableOpacity>

            <View style={styles.quickStats}>
              <View style={styles.statCard}>
                <Ionicons name="cash" size={24} color="#4CAF50" />
                <Text style={styles.statNumber}>₹0</Text>
                <Text style={styles.statLabel}>Earnings</Text>
              </View>
              <View style={styles.statCard}>
                <Ionicons name="cube" size={24} color="#E05A3A" />
                <Text style={styles.statNumber}>0</Text>
                <Text style={styles.statLabel}>Deliveries</Text>
              </View>
            </View>
          </View>
        )}

        {/* How it Works */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How it Works</Text>
          <View style={styles.stepCard}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>1</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepTitle}>{isSender ? 'Post Your Parcel' : 'Go Online'}</Text>
              <Text style={styles.stepSubtitle}>
                {isSender 
                  ? 'Enter pickup & drop location, parcel details'
                  : 'Set your destination and travel mode'}
              </Text>
            </View>
          </View>

          <View style={styles.stepCard}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>2</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepTitle}>{isSender ? 'Get Matched' : 'Accept Request'}</Text>
              <Text style={styles.stepSubtitle}>
                {isSender 
                  ? 'Nearby carriers see your request'
                  : 'See requests along your route'}
              </Text>
            </View>
          </View>

          <View style={styles.stepCard}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>3</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepTitle}>{isSender ? 'Hand Over' : 'Pickup & Deliver'}</Text>
              <Text style={styles.stepSubtitle}>
                {isSender 
                  ? 'Give OTP to carrier at pickup'
                  : 'Verify OTPs, deliver safely'}
              </Text>
            </View>
          </View>

          <View style={styles.stepCard}>
            <View style={styles.stepNumber}>
              <Text style={styles.stepNumberText}>4</Text>
            </View>
            <View style={styles.stepContent}>
              <Text style={styles.stepTitle}>{isSender ? 'Track & Receive' : 'Earn Money'}</Text>
              <Text style={styles.stepSubtitle}>
                {isSender 
                  ? 'Track live and confirm delivery'
                  : 'Get paid cash on delivery'}
              </Text>
            </View>
          </View>
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
    padding: 24,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  logo: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#E05A3A',
    marginBottom: 4,
  },
  greeting: {
    fontSize: 16,
    color: '#666',
  },
  content: {
    padding: 16,
  },
  roleSwitcher: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  roleOption: {
    paddingVertical: 12,
  },
  roleTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  roleSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  roleLabel: {
    fontSize: 14,
    color: '#666',
    marginHorizontal: 8,
  },
  activeRole: {
    fontWeight: '600',
    color: '#E05A3A',
  },
  dividerLine: {
    height: 1,
    backgroundColor: '#e0e0e0',
    marginVertical: 16,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 16,
  },
  primaryCard: {
    backgroundColor: '#E05A3A',
    borderRadius: 16,
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginBottom: 4,
  },
  cardSubtitle: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.9)',
  },
  secondaryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  secondaryCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  secondaryCardSubtitle: {
    fontSize: 14,
    color: '#666',
  },
  quickStats: {
    flexDirection: 'row',
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  stepCard: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  stepNumber: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#E05A3A',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  stepNumberText: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  stepContent: {
    flex: 1,
  },
  stepTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  stepSubtitle: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
});