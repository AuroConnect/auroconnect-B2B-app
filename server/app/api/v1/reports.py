from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.user import User
from app.models.invoice import Invoice
from app.utils.decorators import role_required, roles_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import io
import csv
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/sales', methods=['GET'])
@jwt_required()
def get_sales_report():
    """Get sales report based on user role"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category_id = request.args.get('category_id')
        partner_id = request.args.get('partner_id')
        
        # Parse dates
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            end_date = datetime.now() + timedelta(days=1)
        
        # Build base query based on role
        if current_user.role == 'manufacturer':
            # Manufacturer sees sales to distributors
            base_query = db.session.query(
                Order.seller_id,
                Order.buyer_id,
                OrderItem.product_id,
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.created_at,
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                User.business_name.label('buyer_name')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, Order.buyer_id == User.id
            ).filter(
                Order.seller_id == current_user_id,
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
            
        elif current_user.role == 'distributor':
            # Distributor sees purchases from manufacturers and sales to retailers
            base_query = db.session.query(
                Order.seller_id,
                Order.buyer_id,
                OrderItem.product_id,
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.created_at,
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                User.business_name.label('partner_name')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, or_(Order.seller_id == User.id, Order.buyer_id == User.id)
            ).filter(
                or_(Order.buyer_id == current_user_id, Order.seller_id == current_user_id),
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
            
        elif current_user.role == 'retailer':
            # Retailer sees purchases from distributors
            base_query = db.session.query(
                Order.seller_id,
                Order.buyer_id,
                OrderItem.product_id,
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.created_at,
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                User.business_name.label('seller_name')
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, Order.seller_id == User.id
            ).filter(
                Order.buyer_id == current_user_id,
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        # Apply additional filters
        if category_id:
            base_query = base_query.filter(Product.category_id == category_id)
        
        if partner_id:
            if current_user.role == 'manufacturer':
                base_query = base_query.filter(Order.buyer_id == partner_id)
            elif current_user.role == 'distributor':
                base_query = base_query.filter(
                    or_(Order.seller_id == partner_id, Order.buyer_id == partner_id)
                )
            elif current_user.role == 'retailer':
                base_query = base_query.filter(Order.seller_id == partner_id)
        
        # Execute query
        results = base_query.all()
        
        # Process results
        report_data = {
            'summary': {
                'total_orders': len(set(r[0] for r in results)),  # Unique orders
                'total_quantity': sum(r[3] for r in results),
                'total_revenue': sum(r[5] for r in results),
                'average_order_value': sum(r[5] for r in results) / len(set(r[0] for r in results)) if results else 0
            },
            'by_partner': {},
            'by_product': {},
            'by_month': {},
            'details': []
        }
        
        for row in results:
            # Partner analysis
            partner_id = row[1] if current_user.role == 'manufacturer' else (row[0] if row[0] != current_user_id else row[1])
            partner_name = row[9] if current_user.role == 'manufacturer' else row[9]
            
            if partner_id not in report_data['by_partner']:
                report_data['by_partner'][partner_id] = {
                    'name': partner_name,
                    'total_quantity': 0,
                    'total_revenue': 0,
                    'order_count': 0
                }
            
            report_data['by_partner'][partner_id]['total_quantity'] += row[3]
            report_data['by_partner'][partner_id]['total_revenue'] += row[5]
            report_data['by_partner'][partner_id]['order_count'] += 1
            
            # Product analysis
            product_id = row[2]
            if product_id not in report_data['by_product']:
                report_data['by_product'][product_id] = {
                    'name': row[7],
                    'sku': row[8],
                    'total_quantity': 0,
                    'total_revenue': 0
                }
            
            report_data['by_product'][product_id]['total_quantity'] += row[3]
            report_data['by_product'][product_id]['total_revenue'] += row[5]
            
            # Monthly analysis
            month_key = row[6].strftime('%Y-%m')
            if month_key not in report_data['by_month']:
                report_data['by_month'][month_key] = {
                    'total_quantity': 0,
                    'total_revenue': 0,
                    'order_count': 0
                }
            
            report_data['by_month'][month_key]['total_quantity'] += row[3]
            report_data['by_month'][month_key]['total_revenue'] += row[5]
            report_data['by_month'][month_key]['order_count'] += 1
            
            # Detailed records
            report_data['details'].append({
                'order_id': row[0],
                'partner_id': partner_id,
                'partner_name': partner_name,
                'product_id': product_id,
                'product_name': row[7],
                'product_sku': row[8],
                'quantity': row[3],
                'unit_price': float(row[4]),
                'total_price': float(row[5]),
                'date': row[6].isoformat()
            })
        
        # Convert to lists for JSON serialization
        report_data['by_partner'] = list(report_data['by_partner'].values())
        report_data['by_product'] = list(report_data['by_product'].values())
        report_data['by_month'] = list(report_data['by_month'].items())
        
        return jsonify(report_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to generate sales report', 'error': str(e)}), 500

@reports_bp.route('/export/csv', methods=['GET'])
@jwt_required()
def export_report_csv():
    """Export report as CSV"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get the same data as sales report
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            end_date = datetime.now() + timedelta(days=1)
        
        # Build query (same as sales report)
        if current_user.role == 'manufacturer':
            base_query = db.session.query(
                Order.id.label('order_id'),
                Order.created_at.label('order_date'),
                User.business_name.label('buyer_name'),
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.status
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, Order.buyer_id == User.id
            ).filter(
                Order.seller_id == current_user_id,
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        elif current_user.role == 'distributor':
            base_query = db.session.query(
                Order.id.label('order_id'),
                Order.created_at.label('order_date'),
                User.business_name.label('partner_name'),
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.status
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, or_(Order.seller_id == User.id, Order.buyer_id == User.id)
            ).filter(
                or_(Order.buyer_id == current_user_id, Order.seller_id == current_user_id),
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        elif current_user.role == 'retailer':
            base_query = db.session.query(
                Order.id.label('order_id'),
                Order.created_at.label('order_date'),
                User.business_name.label('seller_name'),
                Product.name.label('product_name'),
                Product.sku.label('product_sku'),
                OrderItem.quantity,
                OrderItem.unit_price,
                OrderItem.total_price,
                Order.status
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).join(
                Product, OrderItem.product_id == Product.id
            ).join(
                User, Order.seller_id == User.id
            ).filter(
                Order.buyer_id == current_user_id,
                Order.status.in_(['DELIVERED', 'SHIPPED']),
                Order.created_at >= start_date,
                Order.created_at < end_date
            )
        else:
            return jsonify({'message': 'Invalid user role'}), 400
        
        results = base_query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        if current_user.role == 'manufacturer':
            writer.writerow(['Order ID', 'Date', 'Buyer', 'Product', 'SKU', 'Quantity', 'Unit Price', 'Total', 'Status'])
        elif current_user.role == 'distributor':
            writer.writerow(['Order ID', 'Date', 'Partner', 'Product', 'SKU', 'Quantity', 'Unit Price', 'Total', 'Status'])
        else:  # retailer
            writer.writerow(['Order ID', 'Date', 'Seller', 'Product', 'SKU', 'Quantity', 'Unit Price', 'Total', 'Status'])
        
        # Write data
        for row in results:
            writer.writerow([
                row[0],
                row[1].strftime('%Y-%m-%d'),
                row[2],
                row[3],
                row[4],
                row[5],
                f"${row[6]:.2f}",
                f"${row[7]:.2f}",
                row[8]
            ])
        
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            as_attachment=True,
            download_name=f'sales_report_{start_date.strftime("%Y%m")}.csv',
            mimetype='text/csv'
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to export report', 'error': str(e)}), 500

@reports_bp.route('/export/pdf', methods=['GET'])
@jwt_required()
def export_report_pdf():
    """Export report as PDF"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        # Get the same data as sales report
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        else:
            end_date = datetime.now() + timedelta(days=1)
        
        # Generate PDF
        pdf_buffer = generate_sales_report_pdf(current_user, start_date, end_date)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'sales_report_{start_date.strftime("%Y%m")}.pdf',
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'message': 'Failed to export report', 'error': str(e)}), 500

def generate_sales_report_pdf(user, start_date, end_date):
    """Generate PDF sales report"""
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
    elements.append(Paragraph(f"Sales Report - {user.business_name}", title_style))
    elements.append(Paragraph(f"Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Get summary data
    if user.role == 'manufacturer':
        summary_query = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            Order.seller_id == user.id,
            Order.status.in_(['DELIVERED', 'SHIPPED']),
            Order.created_at >= start_date,
            Order.created_at < end_date
        )
    elif user.role == 'distributor':
        summary_query = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            or_(Order.buyer_id == user.id, Order.seller_id == user.id),
            Order.status.in_(['DELIVERED', 'SHIPPED']),
            Order.created_at >= start_date,
            Order.created_at < end_date
        )
    else:  # retailer
        summary_query = db.session.query(
            func.count(Order.id).label('total_orders'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.total_price).label('total_revenue')
        ).join(
            OrderItem, Order.id == OrderItem.order_id
        ).filter(
            Order.buyer_id == user.id,
            Order.status.in_(['DELIVERED', 'SHIPPED']),
            Order.created_at >= start_date,
            Order.created_at < end_date
        )
    
    summary_result = summary_query.first()
    
    # Summary table
    summary_data = [
        ['Metric', 'Value'],
        ['Total Orders', summary_result.total_orders or 0],
        ['Total Quantity', summary_result.total_quantity or 0],
        ['Total Revenue', f"${summary_result.total_revenue or 0:.2f}"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(elements)
    return buffer
