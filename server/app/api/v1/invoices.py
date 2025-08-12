from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.invoice import Invoice
from app.utils.decorators import role_required, roles_required
from datetime import datetime, timedelta
import uuid
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

invoices_bp = Blueprint('invoices', __name__)

@invoices_bp.route('/', methods=['GET'])
@jwt_required()
def get_invoices():
    """Get invoices for the current user"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        month = request.args.get('month')
        year = request.args.get('year')
        
        # Base query
        if current_user.role == 'manufacturer':
            # Manufacturer sees invoices for orders they sold
            query = Invoice.query.join(Order).filter(Order.seller_id == current_user_id)
        elif current_user.role == 'distributor':
            # Distributor sees invoices for orders they bought and sold
            query = Invoice.query.join(Order).filter(
                (Order.buyer_id == current_user_id) | (Order.seller_id == current_user_id)
            )
        elif current_user.role == 'retailer':
            # Retailer sees invoices for orders they bought
            query = Invoice.query.join(Order).filter(Order.buyer_id == current_user_id)
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply month/year filter
        if month and year:
            try:
                start_date = datetime(int(year), int(month), 1)
                if int(month) == 12:
                    end_date = datetime(int(year) + 1, 1, 1)
                else:
                    end_date = datetime(int(year), int(month) + 1, 1)
                
                query = query.filter(
                    Invoice.created_at >= start_date,
                    Invoice.created_at < end_date
                )
            except ValueError:
                return jsonify({'message': 'Invalid month/year format'}), 400
        
        # Order by creation date
        query = query.order_by(Invoice.created_at.desc())
        
        invoices = query.all()
        
        return jsonify([invoice.to_dict() for invoice in invoices]), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch invoices', 'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>', methods=['GET'])
@jwt_required()
def get_invoice(invoice_id):
    """Get specific invoice details"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
        
        # Check if user has access to this invoice
        order = Order.query.get(invoice.order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        return jsonify(invoice.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch invoice', 'error': str(e)}), 500

@invoices_bp.route('/<invoice_id>/download', methods=['GET'])
@jwt_required()
def download_invoice(invoice_id):
    """Download invoice as PDF"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        invoice = Invoice.query.get(invoice_id)
        if not invoice:
            return jsonify({'message': 'Invoice not found'}), 404
        
        # Check if user has access to this invoice
        order = Order.query.get(invoice.order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        if order.buyer_id != current_user_id and order.seller_id != current_user_id:
            return jsonify({'message': 'Access denied'}), 403
        
        # Generate PDF
        pdf_buffer = generate_invoice_pdf(invoice)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'invoice_{invoice.invoice_number}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to download invoice', 'error': str(e)}), 500

@invoices_bp.route('/monthly-export', methods=['GET'])
@jwt_required()
def export_monthly_invoices():
    """Export all invoices for a specific month as PDF"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        month = request.args.get('month')
        year = request.args.get('year')
        
        if not month or not year:
            return jsonify({'message': 'Month and year are required'}), 400
        
        try:
            start_date = datetime(int(year), int(month), 1)
            if int(month) == 12:
                end_date = datetime(int(year) + 1, 1, 1)
            else:
                end_date = datetime(int(year), int(month) + 1, 1)
        except ValueError:
            return jsonify({'message': 'Invalid month/year format'}), 400
        
        # Get invoices for the month
        if current_user.role == 'manufacturer':
            invoices = Invoice.query.join(Order).filter(
                Order.seller_id == current_user_id,
                Invoice.created_at >= start_date,
                Invoice.created_at < end_date
            ).all()
        elif current_user.role == 'distributor':
            invoices = Invoice.query.join(Order).filter(
                ((Order.buyer_id == current_user_id) | (Order.seller_id == current_user_id)),
                Invoice.created_at >= start_date,
                Invoice.created_at < end_date
            ).all()
        elif current_user.role == 'retailer':
            invoices = Invoice.query.join(Order).filter(
                Order.buyer_id == current_user_id,
                Invoice.created_at >= start_date,
                Invoice.created_at < end_date
            ).all()
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        if not invoices:
            return jsonify({'message': 'No invoices found for the specified month'}), 404
        
        # Generate combined PDF
        pdf_buffer = generate_monthly_invoices_pdf(invoices, current_user, month, year)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'invoices_{year}_{month:0>2}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to export invoices', 'error': str(e)}), 500

@invoices_bp.route('/generate/<order_id>', methods=['POST'])
@jwt_required()
def generate_invoice_for_order(order_id):
    """Generate invoice for a specific order"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'message': 'Order not found'}), 404
        
        # Check if user is the seller
        if order.seller_id != current_user_id:
            return jsonify({'message': 'Only seller can generate invoice'}), 403
        
        # Check if order is in appropriate status
        if order.status not in ['SHIPPED', 'DELIVERED']:
            return jsonify({'message': 'Invoice can only be generated for shipped or delivered orders'}), 400
        
        # Check if invoice already exists
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return jsonify({'message': 'Invoice already exists for this order'}), 409
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        # Create invoice
        invoice = Invoice(
            id=str(uuid.uuid4()),
            invoice_number=invoice_number,
            order_id=order_id,
            seller_id=order.seller_id,
            buyer_id=order.buyer_id,
            total_amount=order.total_amount,
            tax_amount=0,  # Calculate based on business logic
            shipping_amount=0,  # Calculate based on delivery option
            grand_total=order.total_amount
        )
        
        db.session.add(invoice)
        db.session.commit()
        
        return jsonify({
            'message': 'Invoice generated successfully',
            'invoice': invoice.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to generate invoice', 'error': str(e)}), 500

def generate_invoice_pdf(invoice):
    """Generate PDF for a single invoice"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Get order and user details
    order = Order.query.get(invoice.order_id)
    seller = User.query.get(invoice.seller_id)
    buyer = User.query.get(invoice.buyer_id)
    
    # Title
    elements.append(Paragraph("INVOICE", title_style))
    elements.append(Spacer(1, 20))
    
    # Invoice details
    invoice_data = [
        ['Invoice Number:', invoice.invoice_number],
        ['Date:', invoice.created_at.strftime('%B %d, %Y')],
        ['Order Number:', order.id],
        ['Status:', order.status]
    ]
    
    invoice_table = Table(invoice_data, colWidths=[2*inch, 4*inch])
    invoice_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(invoice_table)
    elements.append(Spacer(1, 20))
    
    # Seller and Buyer information
    seller_buyer_data = [
        ['Seller:', 'Buyer:'],
        [f"{seller.business_name}<br/>Email: {seller.email}", f"{buyer.business_name}<br/>Email: {buyer.email}"]
    ]
    
    seller_buyer_table = Table(seller_buyer_data, colWidths=[3*inch, 3*inch])
    seller_buyer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(seller_buyer_table)
    elements.append(Spacer(1, 20))
    
    # Order items
    items_data = [['Product', 'SKU', 'Quantity', 'Unit Price', 'Total']]
    for item in order.items:
        items_data.append([
            item.product.name,
            item.product.sku,
            str(item.quantity),
            f"${item.unit_price:.2f}",
            f"${item.total_price:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 20))
    
    # Totals
    totals_data = [
        ['Subtotal:', f"${invoice.total_amount:.2f}"],
        ['Tax:', f"${invoice.tax_amount:.2f}"],
        ['Shipping:', f"${invoice.shipping_amount:.2f}"],
        ['Total:', f"${invoice.grand_total:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[4*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(totals_table)
    
    # Build PDF
    doc.build(elements)
    return buffer

def generate_monthly_invoices_pdf(invoices, user, month, year):
    """Generate PDF for monthly invoice export"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # Title
    elements.append(Paragraph(f"Monthly Invoices Report - {month}/{year}", title_style))
    elements.append(Spacer(1, 20))
    
    # Summary table
    summary_data = [['Invoice #', 'Order #', 'Date', 'Amount', 'Status']]
    total_amount = 0
    
    for invoice in invoices:
        order = Order.query.get(invoice.order_id)
        summary_data.append([
            invoice.invoice_number,
            order.id,
            invoice.created_at.strftime('%Y-%m-%d'),
            f"${invoice.grand_total:.2f}",
            order.status
        ])
        total_amount += invoice.grand_total
    
    summary_table = Table(summary_data, colWidths=[1.5*inch, 1.5*inch, 1*inch, 1*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Total
    total_data = [['Total Amount:', f"${total_amount:.2f}"]]
    total_table = Table(total_data, colWidths=[4*inch, 2*inch])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    elements.append(total_table)
    
    # Build PDF
    doc.build(elements)
    return buffer 