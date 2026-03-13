import os
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
import vobject
import secrets

app = Flask(__name__)

# Hardcoded configuration
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'  # Change this!
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = ''

# ========== DATABASE MODELS ==========
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'ip_address': self.ip_address
        }

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Create tables and default admin
with app.app_context():
    db.create_all()

    # HARDCODED ADMIN CREDENTIALS
    ADMIN_USERNAME = "CyberVRTX101"
    ADMIN_PASSWORD = "$CyberVRTX@#10*2"

    if not Admin.query.filter_by(username=ADMIN_USERNAME).first():
        admin = Admin(username=ADMIN_USERNAME)
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Admin created with username: {ADMIN_USERNAME}")

# ========== HELPER FUNCTIONS ==========
def get_client_ip():
    """Get real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr

def validate_phone(phone):
    """Simple phone validation"""
    if not phone:
        return False
    digits = re.sub(r'\D', '', phone)
    return 7 <= len(digits) <= 15

def validate_name(name):
    """Simple name validation"""
    if not name:
        return False
    name = name.strip()
    return 2 <= len(name) <= 50

# ========== SIMPLE SPAM PREVENTION ==========
def check_rate_limit(ip):
    """Check if IP has exceeded submission limit"""
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    count = Contact.query.filter(
        Contact.ip_address == ip,
        Contact.timestamp >= today_start
    ).count()
    return count < 3  # Max 3 per day

# ========== PUBLIC ROUTES ==========
@app.route('/')
def index():
    """Main page - check if user joined channel first"""
    if not session.get('joined_channel'):
        return redirect(url_for('force_join'))
    
    total_contacts = Contact.query.count()
    return render_template('index.html', total_contacts=total_contacts)

@app.route('/force-join')
def force_join():
    """Force join page - users must join channel"""
    return render_template('force-join.html', channel_link="https://t.me/vortexvcf")

@app.route('/verify-join', methods=['POST'])
def verify_join():
    """User confirms they joined the channel"""
    session['joined_channel'] = True
    session.permanent = True
    return jsonify({'success': True, 'redirect': url_for('index')})

@app.route('/api/submit', methods=['POST'])
def submit_contact():
    """Submit contact after joining channel"""
    # Check if user joined channel first
    if not session.get('joined_channel'):
        return jsonify({'error': 'Please join channel first'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid data'}), 400
        
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        
        # Validate inputs
        if not name or not phone:
            return jsonify({'error': 'Name and phone required'}), 400
        
        if not validate_name(name):
            return jsonify({'error': 'Name must be between 2-50 characters'}), 400
        
        if not validate_phone(phone):
            return jsonify({'error': 'Valid phone number required (7-15 digits)'}), 400
        
        # Clean phone number
        clean_phone = re.sub(r'\D', '', phone)
        
        # Get client IP
        ip = get_client_ip()
        
        # Check rate limit
        if not check_rate_limit(ip):
            return jsonify({'error': 'Daily limit reached (3 submissions max)'}), 429
        
        # Save contact
        contact = Contact(
            name=name,
            phone=clean_phone,
            ip_address=ip
        )
        db.session.add(contact)
        db.session.commit()
        
        # Get updated total
        total = Contact.query.count()
        
        # Calculate remaining submissions
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = Contact.query.filter(
            Contact.ip_address == ip,
            Contact.timestamp >= today_start
        ).count()
        remaining = 3 - today_count
        
        return jsonify({
            'success': True,
            'message': 'Contact saved successfully!',
            'total': total,
            'remaining': remaining
        }), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server error occurred'}), 500

# ========== ADMIN ROUTES ==========
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            login_user(admin, remember=True)
            session.permanent = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin.html', error='Invalid credentials')
    
    return render_template('admin.html')

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    total_contacts = Contact.query.count()
    recent_contacts = Contact.query.order_by(Contact.timestamp.desc()).limit(10).all()
    
    today = datetime.utcnow().date()
    today_contacts = Contact.query.filter(
        db.func.date(Contact.timestamp) == today
    ).count()
    
    return render_template('dashboard.html',
                         total=total_contacts,
                         today=today_contacts,
                         recent=recent_contacts)

@app.route('/admin/api/contacts')
@login_required
def get_contacts():
    """Get all contacts (JSON)"""
    contacts = Contact.query.order_by(Contact.timestamp.desc()).all()
    return jsonify([c.to_dict() for c in contacts])

@app.route('/admin/export/csv')
@login_required
def export_csv():
    """Export contacts as CSV"""
    contacts = Contact.query.all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Phone', 'Timestamp', 'IP Address'])
    
    for contact in contacts:
        cw.writerow([
            contact.id,
            contact.name,
            contact.phone,
            contact.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            contact.ip_address
        ])
    
    output = si.getvalue()
    response = app.response_class(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=vortex_contacts.csv'}
    )
    return response

@app.route('/admin/export/vcf')
@login_required
def export_vcf():
    """Export contacts as VCF"""
    contacts = Contact.query.all()
    
    vcf_content = ""
    for contact in contacts:
        v = vobject.vCard()
        v.add('fn').value = contact.name
        v.add('tel').value = contact.phone
        vcf_content += v.serialize()
    
    response = app.response_class(
        vcf_content,
        mimetype='text/vcard',
        headers={'Content-Disposition': 'attachment;filename=vortex_contacts.vcf'}
    )
    return response

# ========== STATS ROUTE (FIX THE 404 ERROR) ==========
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get contact statistics for the frontend"""
    try:
        total = Contact.query.count()
        return jsonify({'total': total})
    except Exception as e:
        return jsonify({'total': 0})

@app.route('/admin/delete/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    """Delete specific contact"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/logout')
@login_required
def logout():
    """Admin logout"""
    logout_user()
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
