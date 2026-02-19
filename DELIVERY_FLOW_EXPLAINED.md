# DELIVERGE - Complete Delivery Flow Documentation

## 📦 How DELIVERGE Works: Real-Life Delivery Scenario

### **SCENARIO**: Raj in Panaji needs to send documents to his friend Maya in Margao

---

## 🚀 SENDER FLOW (Raj's Journey)

### **Step 1: Post Parcel Request**
1. Raj opens DELIVERGE app → Switches to "Sender" mode
2. Taps "Post New Delivery" button
3. **Enters Details**:
   - Pickup: His office in Panaji (15.4909°N, 73.8278°E)
   - Dropoff: Maya's home in Margao (15.2832°N, 73.9685°E)
   - Category: Documents
   - Weight: 0.5 kg
   - Declared Value: ₹500
   - Uploads 2 photos of sealed envelope
   - Timing: Within 2 hours
4. System calculates: Distance = 33 km, Price = ₹157 (₹25 base + ₹4×33)
5. Raj confirms and posts the delivery

### **Step 2: Wait for Match**
- Status: "Posted - Looking for carriers"
- Raj sees his delivery in "My Deliveries" tab
- Push notification will alert when carrier accepts

### **Step 3: Carrier Accepts (Priya going to Margao)**
- Notification: "Carrier found! Priya will deliver your parcel"
- **Raj receives PICKUP OTP: 4825** (displayed prominently on screen)
- Can see Priya's:
  - Name & rating (4.8 ⭐)
  - Vehicle: Car
  - Phone number for WhatsApp contact
- Status changes to: "Matched - Awaiting Pickup"

### **Step 4: Pickup (Physical Handover)**
**Location**: Raj's office parking lot

**What Happens**:
1. Priya arrives at pickup location
2. Priya's app shows: "Enter sender's OTP"
3. **Raj tells Priya verbally: "4825"**
4. Priya enters 4825 in her app
5. System verifies OTP ✅
6. Priya takes a photo of the parcel
7. Status changes to: "Picked Up - In Transit"
8. **Raj hands over the parcel to Priya**

**What Raj Sees**:
- Real-time notification: "Parcel picked up!"
- Live GPS tracking shows Priya's location
- Can chat with Priya in-app if needed

### **Step 5: In Transit**
- Raj tracks Priya's location on map in real-time
- Sees estimated arrival time
- Gets updates: "Carrier is 5 km away from dropoff"

### **Step 6: Delivery to Recipient (Maya)**
**Location**: Maya's home in Margao

**How Maya Gets Notified**:
- Raj shared **Public Tracking Link** with Maya via WhatsApp:
  - `https://deliverge.com/track/delivery_abc123`
- Maya opens link (no app/login needed)
- Sees:
  - Live map showing Priya's location
  - Parcel details
  - **DELIVERY OTP: 7639** (shown clearly)
  - Status updates

**What Happens at Delivery**:
1. Priya reaches Maya's home
2. Priya's app shows: "Enter recipient's OTP"
3. **Maya tells Priya: "7639"**
4. Priya enters 7639 in app
5. System verifies OTP ✅
6. Priya takes proof-of-delivery photo
7. **Maya hands ₹157 cash to Priya**
8. Status changes to: "Delivered ✓"

### **Step 7: Post-Delivery**
- Raj gets notification: "Parcel delivered successfully!"
- Can rate Priya (5 stars)
- Can see delivery receipt with timestamps
- Maya can also rate the experience

---

## 🚗 CARRIER FLOW (Priya's Journey)

### **Before Starting: KYC Verification**

**One-Time Setup**:
1. Priya switches to "Carrier" mode
2. Taps "Complete KYC"
3. Submits:
   - WhatsApp phone: +91 98765 43210
   - Aadhaar card photo (front)
   - Selfie holding Aadhaar
   - Vehicle type: Car
4. Status: "Pending Admin Approval"
5. Admin reviews within 24 hours
6. Priya gets notification: "KYC Approved! You can now go online"

### **Step 1: Going Online**
1. Priya is travelling from Panaji to Margao for work
2. Opens app → Carrier mode
3. Taps "Go Online"
4. Sets destination: Margao (15.2832°N, 73.9685°E)
5. Selects travel mode: Car
6. Status: "Online - Looking for deliveries"

### **Step 2: Sees Nearby Delivery Request**
- **REQUEST CARD APPEARS** with 60-second timer:
  ```
  📦 Documents Delivery
  From: Panaji Office Area
  To: Margao Residential
  Distance: 33 km (2 km detour)
  Earnings: ₹157
  Weight: 0.5 kg
  
  [ACCEPT] [DECLINE]
  ⏱️ 58 seconds remaining
  ```

### **Step 3: Accept Delivery**
- Priya taps "ACCEPT"
- Gets Raj's contact info & pickup location
- **Receives instructions**: "Get 4-digit OTP from sender at pickup"
- Status: "Delivery Accepted - Head to Pickup"

### **Step 4: Pickup**
- Arrives at Raj's office
- Opens delivery screen
- Sees: "Enter sender's pickup OTP"
- **Raj tells her: "4825"**
- Priya enters 4825
- System verifies ✅
- Takes photo of parcel
- **Receives parcel from Raj**
- Status: "In Transit"

### **Step 5: During Transit**
- GPS auto-pings location every 2 minutes
- Raj can see her moving on map
- If Raj messages, she can reply via in-app chat
- SOS button available if any issues

### **Step 6: Delivery**
- Arrives at Maya's home
- Sees: "Enter recipient's delivery OTP"
- **Maya tells her: "7639"**
- Priya enters 7639
- System verifies ✅
- Takes proof-of-delivery photo
- **Collects ₹157 cash from Maya**
- Status: "Delivered"

### **Step 7: Earnings**
- +₹157 added to earnings dashboard
- Can rate sender (Raj) and recipient (Maya)
- Continues journey to original destination
- Can accept more deliveries if available

---

## 🔒 Security Features in Action

### **OTP System**
- **Pickup OTP (4825)**: Sender → Carrier verification
  - Ensures carrier is legitimate
  - Sender won't give parcel without matching carrier
- **Delivery OTP (7639)**: Recipient → Carrier verification
  - Ensures recipient is correct person
  - Carrier won't leave parcel without OTP
- Both OTPs are **single-use** and **expire in 2 hours**

### **Photo Documentation**
1. **Parcel Photos (by Sender)**: Condition before pickup
2. **Pickup Photo (by Carrier)**: Proof of collection
3. **Delivery Photo (by Carrier)**: Proof of handover
4. **All stored in MongoDB for dispute resolution**

### **Real-Time Tracking**
- GPS location every 2 minutes
- Breadcrumb trail stored in database
- If carrier goes offline: "Signal lost - last seen 3 mins ago"
- Automatic alert to admin if offline >10 mins

### **In-App Chat**
- Text-only, per-delivery thread
- No phone number sharing needed
- All messages stored for safety
- Available from "Matched" until "Delivered"

### **Trust Mechanisms**
1. **KYC Verification**: Aadhaar + selfie required
2. **Ratings**: Both parties rate each other after delivery
3. **Admin Monitoring**: Live map shows all active deliveries
4. **Dispute System**: Can raise dispute with photo/chat evidence
5. **Prohibited Items Check**: System warns about banned items

---

## 🎯 Edge Cases Handled

### **Carrier Cancels After Accepting**
- Before pickup: Delivery re-posted, no penalty
- After pickup: Requires admin intervention

### **Wrong OTP Entered 3 Times**
- Delivery flagged
- Admin alerted immediately
- Call to both parties for verification

### **Carrier Doesn't Arrive in Time**
- Auto-reminder after 20 mins of inactivity
- Auto-cancel after 30 mins
- Delivery automatically re-matched

### **GPS Lost During Transit**
- Shows last known location
- "Signal lost" indicator
- Carrier flagged after 3 dropouts/month

### **Parcel Damaged/Lost**
- Recipient refuses delivery
- Dispute raised with photos
- Admin reviews evidence
- Resolution based on declared value & insurance

### **Payment Dispute**
- Carrier: "Recipient didn't pay"
- Recipient: "Already paid"
- Admin checks: OTP timestamp, delivery photo, chat logs
- Video call if needed for resolution

---

## 💰 Payment Flow (Cash-Based Pilot)

### **Current System** (Phase 1)
- **100% cash transactions**
- Sender tells recipient how much to pay
- Recipient pays carrier directly at delivery
- No platform commission during pilot
- Carrier keeps entire fare

### **Why Cash?**
- Zero cost for pilot phase
- Common in Goa for small transactions
- No payment gateway fees
- Trust built through OTP + tracking

### **Future** (Phase 2)
- Digital payments via UPI/cards
- Platform commission: 10-15%
- Automatic split: Carrier gets 85-90%
- Integration with Razorpay/Stripe

---

## 📱 Public Tracking Link

**URL Format**: `https://deliverge.com/track/{delivery_id}`

**Features** (No Login Required):
- ✅ Real-time GPS location of carrier
- ✅ Delivery status updates
- ✅ **Recipient's DELIVERY OTP displayed**
- ✅ Estimated arrival time
- ✅ Sender & carrier names (first name only)
- ✅ Parcel details
- ❌ No chat access (privacy)
- ❌ No personal info visible

**Use Case**:
- Sender shares link with recipient
- Recipient tracks parcel without app
- Gets OTP from link for final handover

---

## 🔄 Status Lifecycle

1. **Posted** → Looking for carriers
2. **Matched** → Carrier assigned, heading to pickup
3. **Picked Up** → Parcel with carrier, in transit
4. **Delivered** → OTP verified, parcel handed over
5. **(Optional) Cancelled** → Before pickup only
6. **(Optional) Disputed** → Issue raised, admin review

---

## 📊 What Gets Stored in Database

### **deliveries table**
- All addresses, coordinates
- Weight, category, declared value
- **pickup_otp_hash** (bcrypt)
- **delivery_otp_hash** (bcrypt)
- Price, distance
- All timestamps (posted, matched, picked up, delivered)
- Photos (parcel, pickup, delivery) as base64

### **locations table**
- GPS breadcrumb trail
- One row every 2 minutes
- (delivery_id, carrier_id, lat, lng, recorded_at)

### **messages table**
- Chat history per delivery
- (delivery_id, sender_id, content, timestamp)

### **ratings table**
- Stars (1-5) + review text
- Bi-directional: sender rates carrier, carrier rates sender

---

## 🎨 User Experience Highlights

### **For Senders (Raj)**
- ⚡ **3 taps** from home to price confirmation
- 📸 Easy photo upload (camera or gallery)
- 🔢 Big, bold OTP display
- 🗺️ Live tracking like Uber
- 💬 Direct chat with carrier
- 📤 Share tracking link via WhatsApp

### **For Carriers (Priya)**
- 🎯 See requests along route only
- ⏱️ 60-second decision window
- 💰 Transparent earnings upfront
- 📱 Simple OTP entry
- 🚗 Doesn't need to change route much
- 💵 Instant cash payment

### **For Recipients (Maya)**
- 🔗 No app needed (tracking link)
- 🔢 OTP clearly visible
- ⏰ Knows exactly when it's arriving
- 💳 Pays cash directly to carrier

---

## ✅ Success Metrics

**Typical Delivery Time**: 1-2 hours (Panaji to Margao)

**Cost Comparison**:
- Professional courier: ₹250-400
- DELIVERGE: ₹157 (37% cheaper)

**Carrier Earnings**:
- ₹157 for 33 km delivery
- Takes ~45 mins (already going there)
- ₹210/hour effective rate

**User Satisfaction**:
- Sender: Gets cheap, fast delivery
- Carrier: Earns from existing trip
- Recipient: Gets real-time updates

---

This document explains the complete real-world flow of how a parcel gets from sender to recipient using DELIVERGE!
