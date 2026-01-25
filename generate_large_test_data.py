import pandas as pd
import random
from faker import Faker
from fpdf import FPDF
import os

fake = Faker()
Faker.seed(42)

OUTPUT_DIR = "test_data_large"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- Configuration ---
NUM_FILES = 20
ROWS_PER_FILE = 250

# Equipment and Process Lists for GMP context
EQUIPMENT = ['HPLC-01', 'HPLC-02', 'GC-05', 'Balance-03', 'Bioreactor-100L', 'Mixer-200L', 'TabletPress-A', 'Autoclave-01']
ACTIONS = ['Login', 'Logout', 'Start Sequence', 'Stop Sequence', 'Abort', 'Data Save', 'Parameter Change', 'Audit Trail Review', 'Delete File']
DEPARTMENTS = ['QC Lab', 'Production', 'Warehouse', 'IT Security', 'QA Assurance']
ERROR_MSGS = ['Connection Timeout', 'Value Out of Spec', 'Integrity Violation', 'Disk Full', 'User Locked', 'Authorized Access']

def generate_csv_excel(filename, file_type):
    data = []
    for _ in range(ROWS_PER_FILE):
        data.append({
            'Timestamp': fake.date_time_this_year().isoformat(),
            'User_ID': fake.user_name(),
            'Full_Name': fake.name(), # PII
            'IP_Address': fake.ipv4(), # PII
            'Equipment_ID': random.choice(EQUIPMENT),
            'Action_Type': random.choice(ACTIONS),
            'Department': random.choice(DEPARTMENTS),
            'Detail': f"{random.choice(ACTIONS)} executed on {random.choice(EQUIPMENT)}. Status: {random.choice(['Success', 'Fail'])}. Msg: {fake.sentence()}"
        })
    
    df = pd.DataFrame(data)
    
    # Randomly rename columns to simulate diversity
    if random.choice([True, False]):
        df.rename(columns={'User_ID': 'Operator', 'Action_Type': 'Event', 'Timestamp': 'DateTime'}, inplace=True)
    
    if file_type == 'csv':
        df.to_csv(os.path.join(OUTPUT_DIR, filename), index=False)
    else:
        df.to_excel(os.path.join(OUTPUT_DIR, filename), index=False)

def generate_txt(filename):
    with open(os.path.join(OUTPUT_DIR, filename), 'w', encoding='utf-8') as f:
        for _ in range(ROWS_PER_FILE):
            line = f"[{fake.date_time_this_year()}] [Sev: {random.choice(['INFO', 'WARN', 'ERROR'])}] User:{fake.user_name()} ({fake.ipv4()}) performed {random.choice(ACTIONS)} on {random.choice(EQUIPMENT)}. Details: {fake.sentence()}\n"
            f.write(line)

def generate_pdf(filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt=f"Audit Report - {filename}", ln=1, align='C')
    
    for i in range(1, 50): # PDF logic is slow, limit pages/lines for prototype but enough to test
        line = f"{i}. [{fake.date()}] User: {fake.name()} accessed {random.choice(EQUIPMENT)}. Result: {random.choice(['Pass', 'Fail'])}"
        pdf.cell(0, 10, txt=line, ln=1)
        
    pdf.output(os.path.join(OUTPUT_DIR, filename))

# --- Main Generation Loop ---
print(f"Generating {NUM_FILES} files in {OUTPUT_DIR}...")

for i in range(1, NUM_FILES + 1):
    ftype = random.choice(['csv', 'xlsx', 'txt', 'pdf'])
    fname = f"mock_audit_log_{i:02d}_{random.choice(DEPARTMENTS).replace(' ', '_')}.{ftype}"
    
    if ftype == 'csv':
        generate_csv_excel(fname, 'csv')
    elif ftype == 'xlsx':
        generate_csv_excel(fname, 'xlsx')
    elif ftype == 'txt':
        generate_txt(fname)
    elif ftype == 'pdf':
        generate_pdf(fname)
        
    print(f"Created: {fname}")

print("Done!")
