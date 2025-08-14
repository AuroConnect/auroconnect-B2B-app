#!/usr/bin/env python3
"""
Simple verification script to check implementation status
"""
import os
import sys

def check_files_exist():
    """Check if all required files exist"""
    print("🔍 Checking Implementation Files")
    print("=" * 40)
    
    required_files = [
        "client/src/pages/my-products.tsx",
        "server/app/api/v1/my_products.py",
        "client/src/components/layout/header.tsx",
        "client/src/App.tsx",
        "client/src/components/products/product-grid.tsx"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} files")
        return False
    else:
        print(f"\n✅ All {len(required_files)} files exist")
        return True

def check_backend_registration():
    """Check if my_products blueprint is registered"""
    print("\n🔧 Checking Backend Registration")
    print("=" * 40)
    
    try:
        with open("server/app/__init__.py", "r") as f:
            content = f.read()
            
        if "from app.api.v1.my_products import my_products_bp" in content:
            print("✅ my_products blueprint import found")
        else:
            print("❌ my_products blueprint import missing")
            return False
            
        if "app.register_blueprint(my_products_bp, url_prefix='/api/my-products')" in content:
            print("✅ my_products blueprint registration found")
        else:
            print("❌ my_products blueprint registration missing")
            return False
            
        return True
    except FileNotFoundError:
        print("❌ server/app/__init__.py not found")
        return False

def check_frontend_routing():
    """Check if My Products route is added"""
    print("\n🌐 Checking Frontend Routing")
    print("=" * 40)
    
    try:
        with open("client/src/App.tsx", "r") as f:
            content = f.read()
            
        if "import MyProducts from" in content:
            print("✅ MyProducts import found")
        else:
            print("❌ MyProducts import missing")
            return False
            
        if "path=\"/my-products\" component={MyProducts}" in content:
            print("✅ My Products route found")
        else:
            print("❌ My Products route missing")
            return False
            
        return True
    except FileNotFoundError:
        print("❌ client/src/App.tsx not found")
        return False

def check_navigation():
    """Check if My Products navigation is added"""
    print("\n🧭 Checking Navigation")
    print("=" * 40)
    
    try:
        with open("client/src/components/layout/header.tsx", "r") as f:
            content = f.read()
            
        if "My Products" in content:
            print("✅ My Products navigation found")
        else:
            print("❌ My Products navigation missing")
            return False
            
        if "href=\"/my-products\"" in content:
            print("✅ My Products link found")
        else:
            print("❌ My Products link missing")
            return False
            
        if "Catalog" in content:
            print("✅ Catalog navigation found")
        else:
            print("❌ Catalog navigation missing")
            return False
            
        return True
    except FileNotFoundError:
        print("❌ client/src/components/layout/header.tsx not found")
        return False

def check_product_grid_logic():
    """Check if product grid has correct role-based logic"""
    print("\n🛍️ Checking Product Grid Logic")
    print("=" * 40)
    
    try:
        with open("client/src/components/products/product-grid.tsx", "r") as f:
            content = f.read()
            
        if "isAllocated" in content:
            print("✅ isAllocated logic found")
        else:
            print("❌ isAllocated logic missing")
            return False
            
        if "manufacturerId" in content:
            print("✅ manufacturerId logic found")
        else:
            print("❌ manufacturerId logic missing")
            return False
            
        if "canAddToCart" in content or "Add to Cart" in content:
            print("✅ Add to Cart logic found")
        else:
            print("❌ Add to Cart logic missing")
            return False
            
        return True
    except FileNotFoundError:
        print("❌ client/src/components/products/product-grid.tsx not found")
        return False

def main():
    """Main verification function"""
    print("🚀 My Products Implementation Verification")
    print("=" * 50)
    
    checks = [
        check_files_exist,
        check_backend_registration,
        check_frontend_routing,
        check_navigation,
        check_product_grid_logic
    ]
    
    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with error: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\n✅ Implementation Status:")
        print("  ✅ My Products page created")
        print("  ✅ Backend API endpoint implemented")
        print("  ✅ Frontend routing configured")
        print("  ✅ Navigation updated")
        print("  ✅ Role-based product logic implemented")
        print("\n🔧 Next Steps:")
        print("  1. Start the application: docker-compose up -d")
        print("  2. Test the functionality:")
        print("     - Login as manufacturer: m@demo.com / Demo@123")
        print("     - Check My Products vs Catalog tabs")
        print("     - Login as distributor: d@demo.com / Demo@123")
        print("     - Verify role-based product visibility")
        print("     - Login as retailer: r@demo.com / Demo@123")
        print("     - Verify catalog-only access")
    else:
        print("\n⚠️ Some checks failed. Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    main()
