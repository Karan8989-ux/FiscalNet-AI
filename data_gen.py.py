import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os  # <--- Yeh zaroori hai folder banane ke liye

# ==========================================
# 0. CREATE DATA FOLDER (Fix for "No Directory" Error)
# ==========================================
if not os.path.exists('data'):
    os.makedirs('data')
    print("✅ Created missing 'data' folder.")

fake = Faker('en_IN')
Faker.seed(42)

# ==========================================
# 1. GENERATE OFFICERS
# ==========================================
print("👮 Generating 15 Officers...")
officers = []

for i in range(1, 16): 
    off_id = f"OFF{100+i}"
    name = fake.name()
    phone = fake.phone_number()
    email = f"{name.split()[0].lower()}@gov.in"
    
    # FRAUD SETUP: OFF103
    if off_id == 'OFF103':
        phone = "9999999999"
        name = "Suresh Kalmadi"

    officers.append({
        "Officer_ID": off_id,
        "Name": name,
        "Department": random.choice(["PWD", "Irrigation", "Transport"]),
        "Phone": phone,
        "Email": email
    })

df_off = pd.DataFrame(officers)
df_off.to_csv("data/officers.csv", index=False)

# ==========================================
# 2. GENERATE VENDORS
# ==========================================
print("🏭 Generating 50 Vendors...")
vendors = []

for i in range(50): 
    ven_id = f"VEN{100+i}"
    company = fake.company()
    owner = fake.name()
    phone = fake.phone_number()
    address = fake.address().replace("\n", ", ")
    reg_date = fake.date_between(start_date='-5y', end_date='-2y')
    
    # FRAUD SETUP 1
    if ven_id == 'VEN105':
        phone = "9999999999"
        company = "Scam Infra Pvt Ltd"
        
    # FRAUD SETUP 2
    if ven_id == 'VEN145':
        reg_date = datetime.now().date() - timedelta(days=10)
        company = "Ghost Shell Trading"

    vendors.append({
        "Vendor_ID": ven_id,
        "Company": company,
        "Owner_Name": owner,
        "Phone": phone,
        "Address": address,
        "Registration_Date": reg_date
    })

df_ven = pd.DataFrame(vendors)
df_ven.to_csv("data/vendors.csv", index=False)

# ==========================================
# 3. GENERATE TRANSACTIONS
# ==========================================
print("💸 Generating Transactions...")
transactions = []

def random_date():
    return fake.date_between(start_date='-1y', end_date='today')

# Normal Transactions
for _ in range(150):
    transactions.append({
        "Transaction_ID": fake.uuid4()[:8],
        "Date": random_date(),
        "Vendor_ID": f"VEN{random.randint(100, 149)}",
        "Officer_ID": f"OFF{random.randint(101, 115)}",
        "Amount": round(random.uniform(10000, 800000), -2)
    })

# Fraud Cases
# 1. Collusion
transactions.append({"Transaction_ID": "FRAUD_LINK_1", "Date": datetime.now().date(), "Vendor_ID": "VEN105", "Officer_ID": "OFF103", "Amount": 500000})

# 2. Smurfing
for k in range(5):
    transactions.append({"Transaction_ID": f"FRAUD_SMURF_{k}", "Date": datetime.now().date(), "Vendor_ID": "VEN108", "Officer_ID": "OFF107", "Amount": 490000})

# 3. High Value
transactions.append({"Transaction_ID": "FRAUD_BIG_1", "Date": random_date(), "Vendor_ID": "VEN110", "Officer_ID": "OFF112", "Amount": 50000000})

# 4. Shell
transactions.append({"Transaction_ID": "FRAUD_SHELL_1", "Date": datetime.now().date(), "Vendor_ID": "VEN145", "Officer_ID": "OFF115", "Amount": 1200000})

df_txn = pd.DataFrame(transactions)
df_txn.to_csv("data/transactions.csv", index=False)

print("✅ Data Generated Successfully inside 'data/' folder!")