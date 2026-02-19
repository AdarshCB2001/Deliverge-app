import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Alert,
  ActivityIndicator,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { Picker } from '@react-native-picker/picker';
import api from '../../utils/api';

export default function KYCScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [phone, setPhone] = useState('');
  const [vehicle, setVehicle] = useState<'bike' | 'car' | 'auto' | 'bus' | 'train' | 'walking'>('bike');
  const [aadhaarPhoto, setAadhaarPhoto] = useState<string | null>(null);
  const [selfiePhoto, setSelfiePhoto] = useState<string | null>(null);

  const pickImage = async (type: 'aadhaar' | 'selfie') => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.3,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        if (type === 'aadhaar') {
          setAadhaarPhoto(base64Image);
        } else {
          setSelfiePhoto(base64Image);
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const handleSubmit = async () => {
    if (!phone.trim() || phone.length < 10) {
      Alert.alert('Error', 'Please enter valid WhatsApp number');
      return;
    }
    if (!aadhaarPhoto) {
      Alert.alert('Error', 'Please upload Aadhaar card photo');
      return;
    }
    if (!selfiePhoto) {
      Alert.alert('Error', 'Please upload selfie with Aadhaar');
      return;
    }

    setLoading(true);
    try {
      await api.post('/carrier/kyc', {
        phone_whatsapp: phone.trim(),
        vehicle_type: vehicle,
        aadhaar_photo_base64: aadhaarPhoto,
        selfie_photo_base64: selfiePhoto,
      });

      Alert.alert(
        'Success!',
        'KYC submitted successfully. You will be notified once admin approves your application (usually within 24 hours).',
        [{ text: 'OK', onPress: () => router.back() }]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to submit KYC');
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
        <Text style={styles.title}>KYC Verification</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.infoCard}>
          <Ionicons name="shield-checkmark" size={32} color="#4CAF50" />
          <Text style={styles.infoText}>
            Complete verification to start earning as a carrier. All data is encrypted and secure.
          </Text>
        </View>

        <Text style={styles.label}>WhatsApp Phone Number *</Text>
        <TextInput
          style={styles.input}
          placeholder="+91 98765 43210"
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
          editable={!loading}
        />
        <Text style={styles.hint}>For order notifications and support</Text>

        <Text style={styles.label}>Vehicle Type *</Text>
        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={vehicle}
            onValueChange={(value) => setVehicle(value)}
            style={styles.picker}
            enabled={!loading}
          >
            <Picker.Item label="🏍️ Bike/Scooter" value="bike" />
            <Picker.Item label="🚗 Car" value="car" />
            <Picker.Item label="🛺 Auto Rickshaw" value="auto" />
            <Picker.Item label="🚌 Bus" value="bus" />
            <Picker.Item label="🚂 Train" value="train" />
            <Picker.Item label="🚶 Walking" value="walking" />
          </Picker>
        </View>

        <Text style={styles.label}>Aadhaar Card Photo *</Text>
        <TouchableOpacity
          style={styles.photoUploadButton}
          onPress={() => pickImage('aadhaar')}
          disabled={loading}
        >
          {aadhaarPhoto ? (
            <Image source={{ uri: aadhaarPhoto }} style={styles.uploadedImage} />
          ) : (
            <>
              <Ionicons name="card" size={40} color="#E05A3A" />
              <Text style={styles.uploadText}>Upload Aadhaar (Front)</Text>
            </>
          )}
        </TouchableOpacity>

        <Text style={styles.label}>Selfie with Aadhaar *</Text>
        <TouchableOpacity
          style={styles.photoUploadButton}
          onPress={() => pickImage('selfie')}
          disabled={loading}
        >
          {selfiePhoto ? (
            <Image source={{ uri: selfiePhoto }} style={styles.uploadedImage} />
          ) : (
            <>
              <Ionicons name="camera" size={40} color="#E05A3A" />
              <Text style={styles.uploadText}>Take Selfie Holding Aadhaar</Text>
            </>
          )}
        </TouchableOpacity>

        <View style={styles.guideCard}>
          <Text style={styles.guideTitle}>📸 Photo Guidelines:</Text>
          <Text style={styles.guideItem}>• Clear, well-lit photos</Text>
          <Text style={styles.guideItem}>• All text on Aadhaar must be readable</Text>
          <Text style={styles.guideItem}>• Face should be visible in selfie</Text>
          <Text style={styles.guideItem}>• No blur or shadows</Text>
        </View>

        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.submitButtonText}>Submit for Verification</Text>
          )}
        </TouchableOpacity>
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
    padding: 16,
  },
  infoCard: {
    backgroundColor: '#E8F5E9',
    flexDirection: 'row',
    padding: 16,
    borderRadius: 12,
    marginBottom: 24,
    alignItems: 'center',
  },
  infoText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 14,
    color: '#2E7D32',
    lineHeight: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 16,
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#333',
  },
  hint: {
    fontSize: 12,
    color: '#999',
    marginTop: 4,
  },
  pickerContainer: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    overflow: 'hidden',
  },
  picker: {
    height: 50,
  },
  photoUploadButton: {
    backgroundColor: '#fff',
    borderWidth: 2,
    borderColor: '#E05A3A',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    marginBottom: 16,
  },
  uploadText: {
    marginTop: 8,
    fontSize: 14,
    fontWeight: '600',
    color: '#E05A3A',
  },
  uploadedImage: {
    width: '100%',
    height: 200,
    borderRadius: 8,
  },
  guideCard: {
    backgroundColor: '#FFF3E0',
    padding: 16,
    borderRadius: 8,
    marginVertical: 16,
  },
  guideTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#F57C00',
    marginBottom: 8,
  },
  guideItem: {
    fontSize: 13,
    color: '#F57C00',
    lineHeight: 22,
  },
  submitButton: {
    backgroundColor: '#E05A3A',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 32,
  },
  submitButtonDisabled: {
    opacity: 0.6,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
