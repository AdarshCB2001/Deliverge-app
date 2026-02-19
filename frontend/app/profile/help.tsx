import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  Linking,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

export default function HelpSupportScreen() {
  const router = useRouter();
  const [expandedFAQ, setExpandedFAQ] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  const faqs = [
    {
      question: 'How does DELIVERGE work?',
      answer: 'DELIVERGE connects people who need to send parcels with travelers going in the same direction. Senders post their delivery requests, and carriers accept them to earn money.',
    },
    {
      question: 'Is it safe to send parcels?',
      answer: 'Yes! All carriers must complete KYC verification with Aadhaar card. We also use OTP verification at both pickup and delivery points. Track your parcel in real-time.',
    },
    {
      question: 'What items can I send?',
      answer: 'You can send documents, clothing, food, electronics, and other legal items under 5kg. Prohibited items include: cash, liquor, weapons, drugs, live animals, and hazardous materials.',
    },
    {
      question: 'How is pricing calculated?',
      answer: 'Pricing is based on distance, weight, and timing. Under 2km has flat fees (₹20-30). Longer distances use: ₹25 base + ₹4/km, with multipliers for weight and peak hours.',
    },
    {
      question: 'How do I pay?',
      answer: 'Currently, all payments are cash-based. Senders pay carriers directly at delivery. Digital payments coming soon!',
    },
    {
      question: 'What if my parcel is damaged?',
      answer: 'You can raise a dispute through the app. Our team reviews evidence (photos, chat logs) and helps resolve issues. Declare item value for insurance.',
    },
    {
      question: 'How do I become a carrier?',
      answer: 'Switch to Carrier mode and complete KYC verification (Aadhaar + selfie + vehicle details). Once approved by admin, you can go online and start earning.',
    },
    {
      question: 'Can I cancel a delivery?',
      answer: 'Yes, both senders and carriers can cancel before pickup. After pickup, cancellation requires mutual agreement or admin intervention.',
    },
  ];

  const handleContactSupport = () => {
    if (!message.trim()) {
      Alert.alert('Error', 'Please enter your message');
      return;
    }

    // In a real app, this would send to support API
    Alert.alert(
      'Message Sent',
      'Thank you for contacting us. Our support team will respond within 24 hours.',
      [{ text: 'OK', onPress: () => setMessage('') }]
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Help & Support</Text>
        <View style={{ width: 40 }} />
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView style={styles.content}>
          {/* Quick Contact */}
          <View style={styles.quickContact}>
            <TouchableOpacity
              style={styles.contactCard}
              onPress={() => Linking.openURL('tel:+918888888888')}
            >
              <Ionicons name="call" size={24} color="#4CAF50" />
              <Text style={styles.contactLabel}>Call Us</Text>
              <Text style={styles.contactValue}>+91 88888 88888</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.contactCard}
              onPress={() => Linking.openURL('https://wa.me/918888888888')}
            >
              <Ionicons name="logo-whatsapp" size={24} color="#25D366" />
              <Text style={styles.contactLabel}>WhatsApp</Text>
              <Text style={styles.contactValue}>Chat Now</Text>
            </TouchableOpacity>
          </View>

          {/* FAQs */}
          <Text style={styles.sectionTitle}>Frequently Asked Questions</Text>
          {faqs.map((faq, index) => (
            <TouchableOpacity
              key={index}
              style={styles.faqCard}
              onPress={() => setExpandedFAQ(expandedFAQ === index ? null : index)}
            >
              <View style={styles.faqHeader}>
                <Text style={styles.faqQuestion}>{faq.question}</Text>
                <Ionicons
                  name={expandedFAQ === index ? 'chevron-up' : 'chevron-down'}
                  size={20}
                  color="#666"
                />
              </View>
              {expandedFAQ === index && (
                <Text style={styles.faqAnswer}>{faq.answer}</Text>
              )}
            </TouchableOpacity>
          ))}

          {/* Contact Form */}
          <Text style={styles.sectionTitle}>Still Need Help?</Text>
          <View style={styles.contactForm}>
            <Text style={styles.formLabel}>Send us a message</Text>
            <TextInput
              style={styles.messageInput}
              placeholder="Describe your issue or question..."
              value={message}
              onChangeText={setMessage}
              multiline
              numberOfLines={4}
              textAlignVertical="top"
            />
            <TouchableOpacity
              style={styles.submitButton}
              onPress={handleContactSupport}
            >
              <Text style={styles.submitButtonText}>Send Message</Text>
            </TouchableOpacity>
          </View>

          {/* Emergency */}
          <View style={styles.emergencyCard}>
            <Ionicons name="warning" size={24} color="#FF5252" />
            <View style={{ flex: 1, marginLeft: 12 }}>
              <Text style={styles.emergencyTitle}>Emergency Support</Text>
              <Text style={styles.emergencyText}>
                For urgent issues during delivery, call our 24/7 helpline: +91 88888 88888
              </Text>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
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
  quickContact: {
    flexDirection: 'row',
    padding: 16,
    gap: 12,
  },
  contactCard: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  contactLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 8,
  },
  contactValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#333',
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginHorizontal: 16,
    marginTop: 8,
    marginBottom: 12,
  },
  faqCard: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    marginBottom: 8,
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
  },
  faqHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  faqQuestion: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginRight: 8,
  },
  faqAnswer: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginTop: 12,
  },
  contactForm: {
    backgroundColor: '#fff',
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  formLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  messageInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#333',
    minHeight: 100,
    marginBottom: 12,
  },
  submitButton: {
    backgroundColor: '#E05A3A',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  emergencyCard: {
    flexDirection: 'row',
    backgroundColor: '#FFEBEE',
    marginHorizontal: 16,
    padding: 16,
    borderRadius: 8,
    marginBottom: 24,
  },
  emergencyTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#D32F2F',
    marginBottom: 4,
  },
  emergencyText: {
    fontSize: 13,
    color: '#C62828',
    lineHeight: 18,
  },
});