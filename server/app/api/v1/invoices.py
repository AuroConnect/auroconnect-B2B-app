from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Order, Invoice, User
import os
from datetime import datetime
import uuid

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/generate/<order_id>', methods=['POST'])
@jwt_required()
def generate_invoice(order_id):
    """Generate invoice PDF for an order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Check if user has access to this order
        if user.role == 'manufacturer':
            if order.seller_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.seller_id != current_user_id and order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Check if order is shipped or delivered
        if order.status not in ['shipped', 'delivered']:
            return jsonify({'message': 'Invoice can only be generated for shipped or delivered orders'}), 400
        
        # Check if invoice already exists
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return jsonify(existing_invoice.to_dict()), 200
        
        # Generate invoice
        invoice_number = Invoice.generate_invoice_number()
        total_amount = order.get_total_price()
        tax_amount = total_amount * 0.1  # 10% tax
        
        # Create invoice directory if it doesn't exist
        invoice_dir = os.path.join(os.getcwd(), 'invoices')
        if not os.path.exists(invoice_dir):
            os.makedirs(invoice_dir)
        
        # Generate PDF filename
        pdf_filename = f"invoice_{invoice_number}_{order_id}.pdf"
        pdf_path = os.path.join(invoice_dir, pdf_filename)
        
        # Generate PDF content (simplified for now)
        pdf_content = generate_pdf_content(order, invoice_number, total_amount, tax_amount)
        
        # Save PDF (in a real implementation, you'd use a PDF library)
        with open(pdf_path, 'w') as f:
            f.write(pdf_content)
        
        # Create invoice record
        new_invoice = Invoice(
            order_id=order_id,
            pdf_url=pdf_path,
            invoice_number=invoice_number,
            total_amount=total_amount + tax_amount,
            tax_amount=tax_amount
        )
        
        db.session.add(new_invoice)
        db.session.commit()
        
        return jsonify(new_invoice.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to generate invoice', 'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get invoice details"""
    try:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
        
        # Check if user has access to this invoice
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        order = invoice.order
        if user.role == 'manufacturer':
            if order.seller_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.seller_id != current_user_id and order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch invoice', 'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>/download', methods=['GET'])
@jwt_required()
def download_invoice(invoice_id):
    """Download invoice PDF"""
    try:
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
        
        # Check if user has access to this invoice
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        order = invoice.order
        if user.role == 'manufacturer':
            if order.seller_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.seller_id != current_user_id and order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        # Check if PDF file exists
        if not os.path.exists(invoice.pdf_url):
            return jsonify({'message': 'PDF file not found'}), 404
        
        return send_file(
            invoice.pdf_url,
            as_attachment=True,
            download_name=f"invoice_{invoice.invoice_number}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to download invoice', 'error': str(e)}), 500

@invoices_bp.route('/order/<order_id>', methods=['GET'])
@jwt_required()
def get_order_invoice(order_id):
    """Get invoice for a specific order"""
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Check if user has access to this order
        if user.role == 'manufacturer':
            if order.seller_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'distributor':
            if order.seller_id != current_user_id and order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        elif user.role == 'retailer':
            if order.buyer_id != current_user_id:
                return jsonify({'message': 'Access denied'}), 403
        
        invoice = Invoice.query.filter_by(order_id=order_id).first()
        if not invoice:
            return jsonify({'message': 'Invoice not found for this order'}), 404
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch invoice', 'error': str(e)}), 500

def generate_pdf_content(order, invoice_number, total_amount, tax_amount):
    """Generate PDF content (simplified)"""
    # This is a simplified version. In a real implementation, you'd use a PDF library like WeasyPrint or pdfkit
    
    content = f"""
INVOICE

Invoice Number: {invoice_number}
Date: {datetime.now().strftime('%Y-%m-%d')}
Order ID: {order.id}

SELLER INFORMATION:
Name: {order.seller.name}
Email: {order.seller.email}
Phone: {order.seller.phone_number or 'N/A'}
Address: {order.seller.address or 'N/A'}

BUYER INFORMATION:
Name: {order.buyer.name}
Email: {order.buyer.email}
Phone: {order.buyer.phone_number or 'N/A'}
Address: {order.buyer.address or 'N/A'}

PRODUCT DETAILS:
Product: {order.product.name if order.product else 'N/A'}
SKU: {order.product.sku if order.product else 'N/A'}
Quantity: {order.quantity}
Unit Price: ${order.product.price if order.product else 0:.2f}
Subtotal: ${total_amount:.2f}
Tax (10%): ${tax_amount:.2f}
Total: ${total_amount + tax_amount:.2f}

ORDER STATUS: {order.status.upper()}

Delivery Method: {order.delivery_method or 'N/A'}
Delivery Address: {order.delivery_address or 'N/A'}

Notes: {order.notes or 'N/A'}

Thank you for your business!
    """
    
    return content

@invoices_bp.route('/my-invoices', methods=['GET'])
@jwt_required()
def get_my_invoices():
    """Get invoices for retailer dashboard"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        if user.role != 'retailer':
            return jsonify({'message': 'Access denied'}), 403
        
        # Get retailer's orders
        orders = Order.query.filter_by(buyer_id=current_user_id).all()
        order_ids = [order.id for order in orders]
        
        # Get invoices for these orders
        invoices = Invoice.query.filter(Invoice.order_id.in_(order_ids)).all()
        
        return jsonify([invoice.to_dict() for invoice in invoices]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch invoices', 'error': str(e)}), 500 