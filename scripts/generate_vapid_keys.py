#!/usr/bin/env python3
"""
Generate VAPID keys for push notifications
Run this script to generate the required VAPID keys for web push notifications
"""

import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend

def generate_vapid_keys():
    """Generate VAPID private and public keys"""
    
    # Generate private key
    private_key = ec.generate_private_key(
        ec.SECP256R1(),
        default_backend()
    )
    
    # Get public key
    public_key = private_key.public_key()
    
    # Serialize private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Convert to base64 for VAPID
    private_key_b64 = base64.urlsafe_b64encode(
        private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    ).decode('utf-8').rstrip('=')
    
    public_key_b64 = base64.urlsafe_b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    ).decode('utf-8').rstrip('=')
    
    return {
        'private_key': private_key_b64,
        'public_key': public_key_b64,
        'private_key_pem': private_key_pem.decode('utf-8'),
        'public_key_pem': public_key_pem.decode('utf-8')
    }

def main():
    """Main function to generate and display VAPID keys"""
    print("🔑 Generating VAPID keys for push notifications...")
    print()
    
    try:
        keys = generate_vapid_keys()
        
        print("✅ VAPID keys generated successfully!")
        print()
        print("📋 Add these to your .env file:")
        print("=" * 50)
        print(f"VAPID_PRIVATE_KEY={keys['private_key']}")
        print(f"VAPID_PUBLIC_KEY={keys['public_key']}")
        print("CONTACT_EMAIL=admin@tinderlike.com")
        print("=" * 50)
        print()
        
        # Save to files
        with open('vapid_private.pem', 'w') as f:
            f.write(keys['private_key_pem'])
        
        with open('vapid_public.pem', 'w') as f:
            f.write(keys['public_key_pem'])
        
        print("💾 Keys also saved to:")
        print("  - vapid_private.pem")
        print("  - vapid_public.pem")
        print()
        print("⚠️  Keep your private key secure and never share it!")
        print("✅ The public key can be shared and is safe to include in your frontend code.")
        
    except Exception as e:
        print(f"❌ Error generating VAPID keys: {e}")
        print()
        print("💡 Make sure you have the cryptography library installed:")
        print("   pip install cryptography")

if __name__ == "__main__":
    main()

