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
  KeyboardAvoidingView,
  Platform,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import * as ImagePicker from 'expo-image-picker';
import { Picker } from '@react-native-picker/picker';
import api from '../../utils/api';

export default function PostParcelScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  // Step 1: Locations
  const [pickupAddress, setPickupAddress] = useState('');
  const [pickupLat, setPickupLat] = useState(15.4909); // Default Panaji
  const [pickupLng, setPickupLng] = useState(73.8278);
  const [dropoffAddress, setDropoffAddress] = useState('');
  const [dropoffLat, setDropoffLat] = useState(15.2832); // Default Margao
  const [dropoffLng, setDropoffLng] = useState(73.9685);

  // Step 2: Parcel Details
  const [category, setCategory] = useState<'documents' | 'clothing' | 'food' | 'electronics' | 'other'>('documents');
  const [weight, setWeight] = useState('');
  const [declaredValue, setDeclaredValue] = useState('');
  const [photos, setPhotos] = useState<string[]>([]);

  // Step 3: Timing
  const [timing, setTiming] = useState<'asap' | 'within_2h' | 'within_4h' | 'scheduled'>('asap');

  // Step 4: Price (calculated)
  const [calculatedPrice, setCalculatedPrice] = useState(0);

  const pickImage = async () => {
    try {
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.5,
        base64: true,
      });

      if (!result.canceled && result.assets[0].base64) {
        const base64Image = `data:image/jpeg;base64,${result.assets[0].base64}`;
        setPhotos([...photos, base64Image]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to pick image');
    }
  };

  const calculateDistance = () => {
    // Haversine formula
    const R = 6371;
    const lat1Rad = (pickupLat * Math.PI) / 180;
    const lat2Rad = (dropoffLat * Math.PI) / 180;
    const dlat = ((dropoffLat - pickupLat) * Math.PI) / 180;
    const dlng = ((dropoffLng - pickupLng) * Math.PI) / 180;

    const a =
      Math.sin(dlat / 2) * Math.sin(dlat / 2) +
      Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(dlng / 2) * Math.sin(dlng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  };

  const calculatePrice = () => {
    const distance = calculateDistance();
    const weightNum = parseFloat(weight) || 0.5;

    let price = 0;
    if (distance < 0.5) {
      price = 20;
    } else if (distance < 1.0) {
      price = 25;
    } else if (distance < 2.0) {
      price = 30;
    } else {
      price = 25 + 4 * distance;
    }

    // Weight multiplier
    if (weightNum >= 2 && weightNum <= 5) {
      price *= 1.2;
    }

    // Timing multiplier
    if (timing === 'asap') {
      price *= 1.15;
    }

    return Math.round(price);
  };

  const handleNextStep = () => {
    if (step === 1) {
      if (!pickupAddress.trim() || !dropoffAddress.trim()) {
        Alert.alert('Error', 'Please enter both pickup and dropoff addresses');
        return;
      }
      setStep(2);
    } else if (step === 2) {
      if (!weight || parseFloat(weight) <= 0 || parseFloat(weight) > 5) {
        Alert.alert('Error', 'Weight must be between 0.1 and 5 kg');
        return;
      }
      if (!declaredValue || parseFloat(declaredValue) <= 0) {
        Alert.alert('Error', 'Please enter declared value');
        return;
      }
      if (photos.length === 0) {
        Alert.alert('Info', 'Please add at least one photo of the parcel');
        return;
      }
      setStep(3);
    } else if (step === 3) {
      const price = calculatePrice();
      setCalculatedPrice(price);
      setStep(4);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const deliveryData = {
        pickup_address: pickupAddress.trim(),
        pickup_lat: pickupLat,
        pickup_lng: pickupLng,
        dropoff_address: dropoffAddress.trim(),
        dropoff_lat: dropoffLat,
        dropoff_lng: dropoffLng,
        parcel_category: category,
        weight_kg: parseFloat(weight),
        declared_value: parseFloat(declaredValue),
        parcel_photos_base64: photos,
        timing_preference: timing,
        scheduled_time: null,
      };

      const response = await api.post('/deliveries', deliveryData);

      Alert.alert(
        'Success!',
        `Your delivery has been posted. Delivery ID: ${response.data.delivery_id}`,
        [
          {
            text: 'OK',
            onPress: () => router.replace('/(tabs)/deliveries'),
          },
        ]
      );
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create delivery');
    } finally {
      setLoading(false);
    }
  };

  const renderStep1 = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Step 1: Pickup & Drop-off Locations</Text>
      
      <Text style={styles.label}>Pickup Address *</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter pickup address in Goa"
        value={pickupAddress}
        onChangeText={setPickupAddress}
      />
      <Text style={styles.hint}>We'll use geocoding to get exact coordinates</Text>

      <Text style={styles.label}>Drop-off Address *</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter drop-off address in Goa"
        value={dropoffAddress}
        onChangeText={setDropoffAddress}
      />

      <View style={styles.distanceCard}>
        <Ionicons name="location" size={24} color="#E05A3A" />
        <Text style={styles.distanceText}>
          Estimated Distance: {calculateDistance().toFixed(1)} km
        </Text>
      </View>
    </View>
  );

  const renderStep2 = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Step 2: Parcel Details</Text>

      <Text style={styles.label}>Category *</Text>
      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={category}
          onValueChange={(value) => setCategory(value)}
          style={styles.picker}
        >
          <Picker.Item label="Documents" value="documents" />
          <Picker.Item label="Clothing" value="clothing" />
          <Picker.Item label="Food" value="food" />
          <Picker.Item label="Electronics" value="electronics" />
          <Picker.Item label="Other" value="other" />
        </Picker>
      </View>

      <Text style={styles.label}>Weight (kg) *</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter weight (max 5kg)"
        value={weight}
        onChangeText={setWeight}
        keyboardType="decimal-pad"
      />

      <Text style={styles.label}>Declared Value (\u20b9) *</Text>
      <TextInput
        style={styles.input}
        placeholder="Enter value for insurance"
        value={declaredValue}
        onChangeText={setDeclaredValue}
        keyboardType="numeric"
      />

      <Text style={styles.label}>Parcel Photos * ({photos.length}/3)</Text>
      <View style={styles.photosContainer}>
        {photos.map((photo, index) => (
          <View key={index} style={styles.photoCard}>
            <Image source={{ uri: photo }} style={styles.photoImage} />
            <TouchableOpacity
              style={styles.removePhotoButton}
              onPress={() => setPhotos(photos.filter((_, i) => i !== index))}
            >
              <Ionicons name="close-circle" size={24} color="#FF5252" />
            </TouchableOpacity>
          </View>
        ))}
        {photos.length < 3 && (
          <TouchableOpacity style={styles.addPhotoButton} onPress={pickImage}>
            <Ionicons name="camera" size={32} color="#E05A3A" />
            <Text style={styles.addPhotoText}>Add Photo</Text>
          </TouchableOpacity>
        )}
      </View>

      <View style={styles.warningCard}>
        <Ionicons name="warning" size={20} color="#FF9800" />
        <Text style={styles.warningText}>
          Prohibited: cash, liquor, weapons, drugs, live animals
        </Text>
      </View>
    </View>
  );

  const renderStep3 = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Step 3: Delivery Timing</Text>

      <TouchableOpacity
        style={[styles.timingCard, timing === 'asap' && styles.timingCardSelected]}
        onPress={() => setTiming('asap')}
      >
        <View style={styles.timingCardContent}>
          <Ionicons name="flash" size={24} color={timing === 'asap' ? '#E05A3A' : '#666'} />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.timingTitle}>ASAP</Text>
            <Text style={styles.timingSubtext}>Deliver as soon as possible</Text>
          </View>
          {timing === 'asap' && <Ionicons name="checkmark-circle" size={24} color="#E05A3A" />}
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.timingCard, timing === 'within_2h' && styles.timingCardSelected]}
        onPress={() => setTiming('within_2h')}
      >
        <View style={styles.timingCardContent}>
          <Ionicons name="time" size={24} color={timing === 'within_2h' ? '#E05A3A' : '#666'} />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.timingTitle}>Within 2 Hours</Text>
            <Text style={styles.timingSubtext}>Flexible timing</Text>
          </View>
          {timing === 'within_2h' && <Ionicons name="checkmark-circle" size={24} color="#E05A3A" />}
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={[styles.timingCard, timing === 'within_4h' && styles.timingCardSelected]}
        onPress={() => setTiming('within_4h')}
      >
        <View style={styles.timingCardContent}>
          <Ionicons name="calendar" size={24} color={timing === 'within_4h' ? '#E05A3A' : '#666'} />
          <View style={{ flex: 1, marginLeft: 12 }}>
            <Text style={styles.timingTitle}>Within 4 Hours</Text>
            <Text style={styles.timingSubtext}>Schedule for later</Text>
          </View>
          {timing === 'within_4h' && <Ionicons name="checkmark-circle" size={24} color="#E05A3A" />}
        </View>
      </TouchableOpacity>
    </View>
  );

  const renderStep4 = () => (
    <View style={styles.stepContent}>
      <Text style={styles.stepTitle}>Step 4: Review & Confirm</Text>

      <View style={styles.summaryCard}>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>From:</Text>
          <Text style={styles.summaryValue}>{pickupAddress.substring(0, 30)}...</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>To:</Text>
          <Text style={styles.summaryValue}>{dropoffAddress.substring(0, 30)}...</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Distance:</Text>
          <Text style={styles.summaryValue}>{calculateDistance().toFixed(1)} km</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Weight:</Text>
          <Text style={styles.summaryValue}>{weight} kg</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Category:</Text>
          <Text style={styles.summaryValue}>{category}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Timing:</Text>
          <Text style={styles.summaryValue}>{timing.replace('_', ' ').toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.priceCard}>
        <Text style={styles.priceLabel}>Total Delivery Charge</Text>
        <Text style={styles.priceValue}>\u20b9{calculatedPrice}</Text>
        <Text style={styles.priceNote}>Pay cash to carrier at delivery</Text>
      </View>

      <View style={styles.noticeCard}>
        <Ionicons name="information-circle" size={20} color="#2196F3" />
        <Text style={styles.noticeText}>
          You'll receive a 4-digit OTP to give to the carrier at pickup
        </Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.title}>Post New Delivery</Text>
        <View style={{ width: 40 }} />
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        {[1, 2, 3, 4].map((s) => (
          <View
            key={s}
            style={[styles.progressDot, step >= s && styles.progressDotActive]}
          />
        ))}
      </View>

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={{ flex: 1 }}
      >
        <ScrollView style={styles.content}>
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
        </ScrollView>

        <View style={styles.footer}>
          {step > 1 && (
            <TouchableOpacity
              style={styles.backStepButton}
              onPress={() => setStep(step - 1)}
            >
              <Text style={styles.backStepButtonText}>Back</Text>
            </TouchableOpacity>
          )}

          <TouchableOpacity
            style={[styles.nextButton, { flex: 1 }]}
            onPress={step === 4 ? handleSubmit : handleNextStep}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.nextButtonText}>
                {step === 4 ? 'Confirm & Post' : 'Next'}
              </Text>
            )}
          </TouchableOpacity>
        </View>
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
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    padding: 16,
    backgroundColor: '#fff',
    gap: 8,
  },
  progressDot: {
    width: 60,
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
  },
  progressDotActive: {
    backgroundColor: '#E05A3A',
  },
  content: {
    flex: 1,
  },
  stepContent: {
    padding: 16,
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginTop: 12,
    marginBottom: 6,
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
    marginBottom: 8,
  },
  distanceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  distanceText: {
    marginLeft: 12,
    fontSize: 14,
    fontWeight: '600',
    color: '#F57C00',
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
  photosContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginTop: 8,
  },
  photoCard: {
    width: 100,
    height: 100,
    borderRadius: 8,
    overflow: 'hidden',
    position: 'relative',
  },
  photoImage: {
    width: '100%',
    height: '100%',
  },
  removePhotoButton: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#fff',
    borderRadius: 12,
  },
  addPhotoButton: {
    width: 100,
    height: 100,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#E05A3A',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  addPhotoText: {
    fontSize: 12,
    color: '#E05A3A',
    marginTop: 4,
  },
  warningCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFF3E0',
    padding: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  warningText: {
    marginLeft: 12,
    fontSize: 13,
    color: '#F57C00',
  },
  timingCard: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
  },
  timingCardSelected: {
    borderColor: '#E05A3A',
    borderWidth: 2,
  },
  timingCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  timingTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  timingSubtext: {
    fontSize: 13,
    color: '#666',
  },
  summaryCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#666',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 1,
    textAlign: 'right',
  },
  priceCard: {
    backgroundColor: '#E8F5E9',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 16,
  },
  priceLabel: {
    fontSize: 14,
    color: '#2E7D32',
    marginBottom: 8,
  },
  priceValue: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#1B5E20',
    marginBottom: 8,
  },
  priceNote: {
    fontSize: 12,
    color: '#4CAF50',
  },
  noticeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#E3F2FD',
    padding: 12,
    borderRadius: 8,
  },
  noticeText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 13,
    color: '#1976D2',
    lineHeight: 18,
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    gap: 12,
  },
  backStepButton: {
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    justifyContent: 'center',
  },
  backStepButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  nextButton: {
    backgroundColor: '#E05A3A',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});
