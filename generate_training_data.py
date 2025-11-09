#!/usr/bin/env python3
"""
Generate sample supplier quality dataset with fraud labels
"""
import pandas as pd
import numpy as np
from pathlib import Path

def generate_supplier_dataset(n_samples=1000, fraud_rate=0.15):
    """Generate synthetic supplier quality dataset"""
    np.random.seed(42)
    
    data = []
    
    for i in range(n_samples):
        # Determine if this is a fraud case
        is_fraud = np.random.random() < fraud_rate
        
        # Generate application ID
        application_id = f"APP-{i+1:06d}"
        
        # Company type
        types = ['Vendor', 'Supplier', 'Contractor', 'Service Provider']
        company_type = np.random.choice(types)
        
        # Company name
        company_names = [
            'TechCorp', 'GlobalSupply', 'QualityGoods', 'PrimeVendor',
            'EliteServices', 'PremiumSupply', 'TrustedPartner', 'SecureVendor',
            'ReliableSource', 'BestProvider', 'TopSupplier', 'AceVendor'
        ]
        company_name = f"{np.random.choice(company_names)} {np.random.randint(100, 9999)}"
        
        # Contact info
        email = f"contact@{company_name.lower().replace(' ', '')}.com"
        phone = f"+1-{np.random.randint(200, 999)}-{np.random.randint(200, 999)}-{np.random.randint(1000, 9999)}"
        
        # Address
        addresses = ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr']
        address = np.random.choice(addresses)
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia']
        city = np.random.choice(cities)
        states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA']
        state = np.random.choice(states)
        zip_code = f"{np.random.randint(10000, 99999)}"
        
        # Tax ID
        tax_id = f"{np.random.randint(10, 99)}-{np.random.randint(1000000, 9999999)}"
        
        # Industry
        industries = [
            'Technology', 'Manufacturing', 'Healthcare', 'Finance',
            'Retail', 'Logistics', 'Energy', 'Construction'
        ]
        industry = np.random.choice(industries)
        
        # Security features - fraud cases have fewer security measures
        if is_fraud:
            # Fraud cases: lower probability of security features
            mfa_enabled = np.random.random() < 0.3
            sso_support = np.random.random() < 0.2
            rbac_implemented = np.random.random() < 0.25
            encryption_at_rest = np.random.random() < 0.4
            encryption_in_transit = np.random.random() < 0.5
            key_management = np.random.random() < 0.3
            firewall_enabled = np.random.random() < 0.6
            vpn_required = np.random.random() < 0.2
            ip_whitelisting = np.random.random() < 0.25
            audit_logging = np.random.random() < 0.4
            siem_integration = np.random.random() < 0.2
            alerting_enabled = np.random.random() < 0.3
            gdpr_compliant = np.random.random() < 0.3
            soc2_certified = np.random.random() < 0.1
            iso_compliant = np.random.random() < 0.2
        else:
            # Normal cases: higher probability of security features
            mfa_enabled = np.random.random() < 0.85
            sso_support = np.random.random() < 0.75
            rbac_implemented = np.random.random() < 0.80
            encryption_at_rest = np.random.random() < 0.90
            encryption_in_transit = np.random.random() < 0.95
            key_management = np.random.random() < 0.70
            firewall_enabled = np.random.random() < 0.95
            vpn_required = np.random.random() < 0.60
            ip_whitelisting = np.random.random() < 0.65
            audit_logging = np.random.random() < 0.85
            siem_integration = np.random.random() < 0.70
            alerting_enabled = np.random.random() < 0.80
            gdpr_compliant = np.random.random() < 0.75
            soc2_certified = np.random.random() < 0.50
            iso_compliant = np.random.random() < 0.60
        
        data.append({
            'application_id': application_id,
            'type': company_type,
            'company_name': company_name,
            'email': email,
            'phone': phone,
            'address': address,
            'city': city,
            'state': state,
            'zip': zip_code,
            'tax_id': tax_id,
            'industry': industry,
            'mfaEnabled': int(mfa_enabled),
            'ssoSupport': int(sso_support),
            'rbacImplemented': int(rbac_implemented),
            'encryptionAtRest': int(encryption_at_rest),
            'encryptionInTransit': int(encryption_in_transit),
            'keyManagement': int(key_management),
            'firewallEnabled': int(firewall_enabled),
            'vpnRequired': int(vpn_required),
            'ipWhitelisting': int(ip_whitelisting),
            'auditLogging': int(audit_logging),
            'siemIntegration': int(siem_integration),
            'alertingEnabled': int(alerting_enabled),
            'gdprCompliant': int(gdpr_compliant),
            'soc2Certified': int(soc2_certified),
            'isoCompliant': int(iso_compliant),
            'is_fraud': int(is_fraud)
        })
    
    df = pd.DataFrame(data)
    return df

def main():
    """Generate and save supplier quality dataset"""
    print("="*50)
    print("Generating Supplier Quality Dataset")
    print("="*50)
    
    # Create data directory
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    # Generate dataset
    print("\nGenerating 1000 supplier records...")
    df = generate_supplier_dataset(n_samples=1000, fraud_rate=0.15)
    
    # Save to CSV
    output_path = data_dir / 'supplier_quality_data.csv'
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset saved to {output_path}")
    print(f"\nDataset Summary:")
    print(f"  Total records: {len(df)}")
    print(f"  Fraud cases: {df['is_fraud'].sum()} ({df['is_fraud'].sum() / len(df) * 100:.2f}%)")
    print(f"  Normal cases: {(df['is_fraud'] == 0).sum()} ({(df['is_fraud'] == 0).sum() / len(df) * 100:.2f}%)")
    print(f"  Columns: {len(df.columns)}")
    print("\nSecurity Features Summary (Fraud vs Normal):")
    
    security_cols = ['mfaEnabled', 'ssoSupport', 'rbacImplemented', 'encryptionAtRest',
                   'encryptionInTransit', 'keyManagement', 'firewallEnabled', 'vpnRequired',
                   'ipWhitelisting', 'auditLogging', 'siemIntegration', 'alertingEnabled',
                   'gdprCompliant', 'soc2Certified', 'isoCompliant']
    
    fraud_df = df[df['is_fraud'] == 1]
    normal_df = df[df['is_fraud'] == 0]
    
    print(f"\n  Fraud cases average security score: {fraud_df[security_cols].mean(axis=1).mean():.2f}/15")
    print(f"  Normal cases average security score: {normal_df[security_cols].mean(axis=1).mean():.2f}/15")
    
    print("\n" + "="*50)
    print("Dataset generation complete!")
    print("="*50)

if __name__ == '__main__':
    main()

