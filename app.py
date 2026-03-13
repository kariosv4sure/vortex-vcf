import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import csv
from io import StringIO
import vobject
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
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

# Admin Model
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Contact Model
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
    if not Admin.query.filter_by(username=os.getenv('ADMIN_USERNAME', 'CyberVRTX101')).first():
        admin = Admin(username=os.getenv('ADMIN_USERNAME', 'CyberVRTX101'))
        admin.set_password(os.getenv('ADMIN_PASSWORD', '$CyberVRTX@#10*2'))
        db.session.add(admin)
        db.session.commit()

# ========== PUBLIC ROUTES ==========
@app.route('/')
def index():
    total_contacts = Contact.query.count()
    return render_template('index.html', total_contacts=total_contacts)

@app.route('/api/submit', methods=['POST'])
def submit_contact():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        
        if not name or not phone:
            return jsonify({'error': 'Name and phone required'}), 400
        
        # Save contact
        contact = Contact(
            name=name, 
            phone=phone,
            ip_address=request.remote_addr
        )
        db.session.add(contact)
        db.session.commit()
        
        # Get updated total
        total = Contact.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Contact saved!',
            'total': total
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== ADMIN ROUTES ==========
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
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
    contacts = Contact.query.order_by(Contact.timestamp.desc()).all()
    return jsonify([c.to_dict() for c in contacts])

@app.route('/admin/export/csv')
@login_required
def export_csv():
    contacts = Contact.query.all()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Phone', 'Timestamp', 'IP Address'])
    
    for contact in contacts:
        cw.writerow([
            contact.id, 
            contact.name, 
            contact.phone, 
            contact.timestamp,
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

@app.route('/admin/delete/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/admin/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=False)
