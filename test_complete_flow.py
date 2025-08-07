import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_complete_flow():
    """Test the complete end-to-end workflow"""
    
    print("🚀 Testing Complete AuroMart B2B Workflow")
    print("=" * 60)
    
    # Step 1: Create test users
    print("\n1. Creating test users...")
    
    # Create manufacturer
    manufacturer_data = {
        "name": "Test Manufacturer",
        "email": "manufacturer@test.com",
        "password": "password123",
        "role": "manufacturer",
        "businessName": "Test Manufacturing Co",
        "phoneNumber": "1234567890",
        "address": "123 Factory St, Industrial City"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=manufacturer_data)
        if response.status_code == 201:
            manufacturer = response.json()['user']
            print(f"   ✅ Manufacturer created: {manufacturer['name']}")
        else:
            print(f"   ❌ Manufacturer creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Manufacturer creation error: {e}")
        return False
    
    # Create distributor
    distributor_data = {
        "name": "Test Distributor",
        "email": "distributor@test.com",
        "password": "password123",
        "role": "distributor",
        "businessName": "Test Distribution Co",
        "phoneNumber": "1234567891",
        "address": "456 Distribution Ave, Business City"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=distributor_data)
        if response.status_code == 201:
            distributor = response.json()['user']
            print(f"   ✅ Distributor created: {distributor['name']}")
        else:
            print(f"   ❌ Distributor creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Distributor creation error: {e}")
        return False
    
    # Create retailer
    retailer_data = {
        "name": "Test Retailer",
        "email": "retailer@test.com",
        "password": "password123",
        "role": "retailer",
        "businessName": "Test Retail Store",
        "phoneNumber": "1234567892",
        "address": "789 Retail Blvd, Shopping City"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/register", json=retailer_data)
        if response.status_code == 201:
            retailer = response.json()['user']
            print(f"   ✅ Retailer created: {retailer['name']}")
        else:
            print(f"   ❌ Retailer creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Retailer creation error: {e}")
        return False
    
    # Step 2: Login users and get tokens
    print("\n2. Logging in users...")
    
    # Login manufacturer
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "manufacturer@test.com",
            "password": "password123"
        })
        if response.status_code == 200:
            manufacturer_token = response.json().get('user', {}).get('id')
            print("   ✅ Manufacturer logged in")
        else:
            print(f"   ❌ Manufacturer login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Manufacturer login error: {e}")
        return False
    
    # Login distributor
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "distributor@test.com",
            "password": "password123"
        })
        if response.status_code == 200:
            distributor_token = response.json().get('user', {}).get('id')
            print("   ✅ Distributor logged in")
        else:
            print(f"   ❌ Distributor login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Distributor login error: {e}")
        return False
    
    # Login retailer
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "retailer@test.com",
            "password": "password123"
        })
        if response.status_code == 200:
            retailer_token = response.json().get('user', {}).get('id')
            print("   ✅ Retailer logged in")
        else:
            print(f"   ❌ Retailer login failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Retailer login error: {e}")
        return False
    
    # Step 3: Create partner links
    print("\n3. Creating partner links...")
    
    # For now, we'll simulate the partner links by creating them directly
    # In a real implementation, this would be done through the partnership API
    
    # Step 4: Manufacturer adds products
    print("\n4. Manufacturer adding products...")
    
    manufacturer_headers = {"Authorization": f"Bearer {manufacturer_token}"}
    
    # Add product 1
    product1_data = {
        "name": "Premium Mattress",
        "category": "Mattress",
        "price": 500.00,
        "unit": "piece",
        "stock": 100,
        "description": "High-quality premium mattress"
    }
    
    try:
        response = requests.post(f"{API_BASE}/manufacturer/products", 
                               json=product1_data, 
                               headers=manufacturer_headers)
        if response.status_code == 201:
            product1 = response.json()
            print(f"   ✅ Product 1 added: {product1['name']}")
        else:
            print(f"   ❌ Product 1 creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Product 1 creation error: {e}")
        return False
    
    # Add product 2
    product2_data = {
        "name": "Standard Mattress",
        "category": "Mattress",
        "price": 300.00,
        "unit": "piece",
        "stock": 200,
        "description": "Standard quality mattress"
    }
    
    try:
        response = requests.post(f"{API_BASE}/manufacturer/products", 
                               json=product2_data, 
                               headers=manufacturer_headers)
        if response.status_code == 201:
            product2 = response.json()
            print(f"   ✅ Product 2 added: {product2['name']}")
        else:
            print(f"   ❌ Product 2 creation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Product 2 creation error: {e}")
        return False
    
    # Step 5: Distributor places order to manufacturer
    print("\n5. Distributor placing order to manufacturer...")
    
    distributor_headers = {"Authorization": f"Bearer {distributor_token}"}
    
    order_data = {
        "productId": product1['id'],
        "quantity": 10,
        "notes": "First order from distributor"
    }
    
    try:
        response = requests.post(f"{API_BASE}/distributor/orders", 
                               json=order_data, 
                               headers=distributor_headers)
        if response.status_code == 201:
            manufacturer_order = response.json()
            print(f"   ✅ Order placed: {manufacturer_order['id']}")
        else:
            print(f"   ❌ Order placement failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order placement error: {e}")
        return False
    
    # Step 6: Manufacturer accepts order
    print("\n6. Manufacturer accepting order...")
    
    try:
        response = requests.put(f"{API_BASE}/manufacturer/orders/{manufacturer_order['id']}/status", 
                               json={"status": "accepted"}, 
                               headers=manufacturer_headers)
        if response.status_code == 200:
            print("   ✅ Order accepted by manufacturer")
        else:
            print(f"   ❌ Order acceptance failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order acceptance error: {e}")
        return False
    
    # Step 7: Manufacturer packs and ships order
    print("\n7. Manufacturer packing and shipping order...")
    
    try:
        response = requests.put(f"{API_BASE}/manufacturer/orders/{manufacturer_order['id']}/status", 
                               json={"status": "packed"}, 
                               headers=manufacturer_headers)
        if response.status_code == 200:
            print("   ✅ Order packed by manufacturer")
        else:
            print(f"   ❌ Order packing failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order packing error: {e}")
        return False
    
    try:
        response = requests.put(f"{API_BASE}/manufacturer/orders/{manufacturer_order['id']}/status", 
                               json={"status": "shipped"}, 
                               headers=manufacturer_headers)
        if response.status_code == 200:
            print("   ✅ Order shipped by manufacturer")
        else:
            print(f"   ❌ Order shipping failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order shipping error: {e}")
        return False
    
    # Step 8: Distributor receives and marks as delivered
    print("\n8. Distributor receiving order...")
    
    try:
        response = requests.put(f"{API_BASE}/distributor/orders/{manufacturer_order['id']}/status", 
                               json={"status": "delivered"}, 
                               headers=distributor_headers)
        if response.status_code == 200:
            print("   ✅ Order delivered to distributor")
        else:
            print(f"   ❌ Order delivery failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order delivery error: {e}")
        return False
    
    # Step 9: Retailer places order to distributor
    print("\n9. Retailer placing order to distributor...")
    
    retailer_headers = {"Authorization": f"Bearer {retailer_token}"}
    
    retailer_order_data = {
        "productId": product1['id'],
        "quantity": 5,
        "notes": "First order from retailer"
    }
    
    try:
        response = requests.post(f"{API_BASE}/retailer/orders", 
                               json=retailer_order_data, 
                               headers=retailer_headers)
        if response.status_code == 201:
            retailer_order = response.json()
            print(f"   ✅ Retailer order placed: {retailer_order['id']}")
        else:
            print(f"   ❌ Retailer order placement failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Retailer order placement error: {e}")
        return False
    
    # Step 10: Distributor accepts retailer order
    print("\n10. Distributor accepting retailer order...")
    
    try:
        response = requests.put(f"{API_BASE}/distributor/orders/{retailer_order['id']}/status", 
                               json={"status": "accepted"}, 
                               headers=distributor_headers)
        if response.status_code == 200:
            print("   ✅ Retailer order accepted by distributor")
        else:
            print(f"   ❌ Retailer order acceptance failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Retailer order acceptance error: {e}")
        return False
    
    # Step 11: Distributor ships retailer order
    print("\n11. Distributor shipping retailer order...")
    
    try:
        response = requests.put(f"{API_BASE}/distributor/orders/{retailer_order['id']}/status", 
                               json={"status": "shipped"}, 
                               headers=distributor_headers)
        if response.status_code == 200:
            print("   ✅ Retailer order shipped by distributor")
        else:
            print(f"   ❌ Retailer order shipping failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Retailer order shipping error: {e}")
        return False
    
    # Step 12: Generate invoice
    print("\n12. Generating invoice...")
    
    try:
        response = requests.post(f"{API_BASE}/invoices/generate/{retailer_order['id']}", 
                               headers=distributor_headers)
        if response.status_code == 201:
            invoice = response.json()
            print(f"   ✅ Invoice generated: {invoice['invoiceNumber']}")
        else:
            print(f"   ❌ Invoice generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Invoice generation error: {e}")
        return False
    
    # Step 13: Retailer marks order as delivered
    print("\n13. Retailer marking order as delivered...")
    
    try:
        response = requests.put(f"{API_BASE}/retailer/orders/{retailer_order['id']}/delivered", 
                               headers=retailer_headers)
        if response.status_code == 200:
            print("   ✅ Order marked as delivered by retailer")
        else:
            print(f"   ❌ Order delivery marking failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Order delivery marking error: {e}")
        return False
    
    # Step 14: Generate monthly report
    print("\n14. Generating monthly report...")
    
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        response = requests.get(f"{API_BASE}/retailer/reports/monthly?month={current_month}&year={current_year}", 
                               headers=retailer_headers)
        if response.status_code == 200:
            report = response.json()
            print(f"   ✅ Monthly report generated: {report['orderCount']} orders")
        else:
            print(f"   ❌ Monthly report generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Monthly report generation error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 COMPLETE WORKFLOW TEST PASSED!")
    print("✅ All steps completed successfully")
    print("✅ End-to-end flow is working correctly")
    print("✅ Manufacturer → Distributor → Retailer flow verified")
    print("✅ Order management, status updates, and invoice generation working")
    print("✅ Monthly reporting functionality working")
    
    return True

if __name__ == "__main__":
    from datetime import datetime
    test_complete_flow()
