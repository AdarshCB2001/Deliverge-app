import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Linking,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function AboutScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>About</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* Logo & Name */}
        <View style={styles.logoContainer}>
          <View style={styles.logo}>
            <Ionicons name="cube" size={48} color="#fff" />
          </View>
          <Text style={styles.appName}>DELIVERGE</Text>
          <Text style={styles.tagline}>Peer-to-Peer Parcel Delivery</Text>
          <Text style={styles.version}>Version 1.0.0</Text>
        </View>

        {/* Mission */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Our Mission</Text>
          <Text style={styles.sectionText}>
            DELIVERGE is revolutionizing parcel delivery in Goa by connecting people who need to send parcels with travelers already heading in the same direction. We're making delivery affordable, eco-friendly, and community-driven.
          </Text>
        </View>

        {/* How It Works */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>How It Works</Text>
          <View style={styles.featureItem}>
            <Ionicons name="cube-outline" size={24} color="#E05A3A" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>Senders Post Parcels</Text>
              <Text style={styles.featureDesc}>Need to send something? Post your parcel with pickup and drop-off locations.</Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Ionicons name="car-outline" size={24} color="#E05A3A" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>Carriers Earn Money</Text>
              <Text style={styles.featureDesc}>Already traveling? Accept delivery requests along your route and earn cash.</Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Ionicons name="shield-checkmark-outline" size={24} color="#E05A3A" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>Safe & Secure</Text>
              <Text style={styles.featureDesc}>KYC-verified carriers, OTP verification, real-time tracking, and in-app chat.</Text>
            </View>
          </View>

          <View style={styles.featureItem}>
            <Ionicons name="cash-outline" size={24} color="#E05A3A" />
            <View style={styles.featureText}>
              <Text style={styles.featureTitle}>Transparent Pricing</Text>
              <Text style={styles.featureDesc}>Fair, distance-based pricing. Flat fees for short distances, no hidden charges.</Text>
            </View>
          </View>
        </View>

        {/* Why DELIVERGE */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Why Choose DELIVERGE?</Text>
          <View style={styles.benefitItem}>
            <Ionicons name="flash" size={20} color="#4CAF50" />
            <Text style={styles.benefitText}>Faster than traditional couriers</Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="wallet" size={20} color="#4CAF50" />
            <Text style={styles.benefitText}>More affordable rates</Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="leaf" size={20} color="#4CAF50" />
            <Text style={styles.benefitText}>Eco-friendly (uses existing trips)</Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="people" size={20} color="#4CAF50" />
            <Text style={styles.benefitText}>Community-driven platform</Text>
          </View>
          <View style={styles.benefitItem}>
            <Ionicons name="location" size={20} color="#4CAF50" />
            <Text style={styles.benefitText}>Real-time tracking</Text>
          </View>
        </View>

        {/* Contact */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Contact Us</Text>
          <TouchableOpacity
            style={styles.contactItem}
            onPress={() => Linking.openURL('mailto:support@deliverge.com')}
          >
            <Ionicons name="mail" size={20} color="#666" />
            <Text style={styles.contactText}>support@deliverge.com</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.contactItem}
            onPress={() => Linking.openURL('tel:+918888888888')}
          >
            <Ionicons name="call" size={20} color="#666" />
            <Text style={styles.contactText}>+91 88888 88888</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.contactItem}
            onPress={() => Linking.openURL('https://deliverge.com')}
          >
            <Ionicons name="globe" size={20} color="#666" />
            <Text style={styles.contactText}>www.deliverge.com</Text>
          </TouchableOpacity>
        </View>

        {/* Legal */}
        <View style={styles.legalSection}>
          <TouchableOpacity style={styles.legalItem}>
            <Text style={styles.legalText}>Terms of Service</Text>
            <Ionicons name="chevron-forward" size={20} color="#999" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.legalItem}>
            <Text style={styles.legalText}>Privacy Policy</Text>
            <Ionicons name="chevron-forward" size={20} color="#999" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.legalItem}>
            <Text style={styles.legalText}>Community Guidelines</Text>
            <Ionicons name="chevron-forward" size={20} color="#999" />
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Made with ❤️ in Goa</Text>
          <Text style={styles.footerText}>© 2025 DELIVERGE. All rights reserved.</Text>
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
    flex: 1,
  },
  logoContainer: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  logo: {
    width: 80,
    height: 80,
    borderRadius: 20,
    backgroundColor: '#E05A3A',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  appName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  tagline: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  version: {
    fontSize: 12,
    color: '#999',
  },
  section: {
    padding: 16,
    marginBottom: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  sectionText: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  featureItem: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  featureText: {
    flex: 1,
    marginLeft: 12,
  },
  featureTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  featureDesc: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  benefitText: {
    marginLeft: 12,
    fontSize: 14,
    color: '#333',
  },
  contactItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
  },
  contactText: {
    marginLeft: 12,
    fontSize: 14,
    color: '#E05A3A',
  },
  legalSection: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  legalItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  legalText: {
    fontSize: 14,
    color: '#333',
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 24,
  },
  footerText: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
});