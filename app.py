from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wfd_logger.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def get_valid_arrl_sections():
    """Get list of valid ARRL sections"""
    return [
        # US State Sections
        'AL', 'AK', 'AZ', 'AR', 'CO', 'CT', 'DE', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 
        'KY', 'LA', 'ME', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NM', 'NC', 'ND', 
        'OH', 'OK', 'OR', 'RI', 'SC', 'SD', 'TN', 'UT', 'VT', 'WA', 'WV', 'WI', 'WY',
        
        # Multi-section States
        'EB', 'LAX', 'ORG', 'SB', 'SCV', 'SF', 'SJV', 'SV', 'PAC',  # California
        'WCF', 'NFL', 'SFL',  # Florida
        'MDC',  # Maryland-DC
        'MA', 'EMA',  # Massachusetts
        'NNJ', 'SNJ',  # New Jersey
        'NYC', 'LI', 'NLI', 'WNY',  # New York
        'EPA', 'WPA',  # Pennsylvania
        'NTX', 'STX', 'WTX',  # Texas
        'VA',  # Virginia
        
        # Special sections
        'NY',  # New York (general)
        'CA',  # California (general)
        'TX',  # Texas (general)
        'FL',  # Florida (general)
        'PA',  # Pennsylvania (general)
        'NJ',  # New Jersey (general)
        'MA',  # Massachusetts (already included)
        
        # Canadian sections
        'AB', 'BC', 'MB', 'NB', 'NL', 'NT', 'NS', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'
    ]

def validate_wfd_exchange(exchange):
    """Validate Winter Field Day exchange format"""
    if not exchange or not exchange.strip():
        return False, "Exchange is required"
    
    exchange = exchange.strip().upper()
    parts = exchange.split()
    
    if len(parts) != 2:
        return False, "Exchange must have exactly 2 parts: category and section (e.g., '2M EPA', '1H GA')"
    
    category, section = parts
    
    # Validate category format - now [number][class] where class is H/I/O/M
    if not re.match(r'^[1-9]\d*[HIOM]$', category):
        return False, f"Invalid category '{category}'. Must be number + class letter (H/I/O/M) like '1H', '2I', '3O', '4M'"
    
    # Valid category letters for WFD 2026
    valid_category_letters = {'H', 'I', 'O', 'M'}  # H=Home, I=Indoor, O=Outdoor, M=Mobile
    if category[-1] not in valid_category_letters:
        return False, f"Invalid class letter '{category[-1]}'. Must be H (Home), I (Indoor), O (Outdoor), or M (Mobile)"
    
    # Validate ARRL section
    valid_sections = get_valid_arrl_sections()
    if section not in valid_sections and section not in ['MX', 'DX']:
        return False, f"Invalid location '{section}'. Must be a valid ARRL/RAC section, 'MX' (Mexico), or 'DX' (other)"
    
    return True, "Valid exchange"

def extract_arrl_section(exchange_received):
    """Extract ARRL section from exchange received (e.g., "2I WI" -> "WI")"""
    if not exchange_received:
        return None
    
    valid_sections = get_valid_arrl_sections()
    
    # Try to extract section from exchange (e.g., "2I WI" -> "WI")
    exchange_parts = exchange_received.strip().split()
    if len(exchange_parts) >= 2:
        potential_section = exchange_parts[-1].upper()
        # Accept ARRL/RAC sections, Mexico (MX), or DX
        if potential_section in valid_sections or potential_section in ['MX', 'DX']:
            return potential_section
    
    return None

def get_arrl_section_timezone(arrl_section):
    """Get timezone for ARRL section"""
    if not arrl_section:
        return 'America/New_York'  # Default to Eastern
    
    section = arrl_section.upper()
    
    # Pacific Time (UTC-8/-7)
    pacific_sections = {
        'WA', 'OR', 'NV', 'CA', 'EB', 'LAX', 'ORG', 'SB', 'SCV', 'SF', 'SJV', 'SV', 'PAC'
    }
    
    # Mountain Time (UTC-7/-6)
    mountain_sections = {
        'AZ', 'CO', 'ID', 'MT', 'NM', 'UT', 'WY'
    }
    
    # Central Time (UTC-6/-5)  
    central_sections = {
        'AL', 'AR', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'MN', 'MS', 'MO', 'NE', 'ND', 
        'OK', 'SD', 'TN', 'TX', 'NTX', 'STX', 'WTX', 'WI'
    }
    
    # Eastern Time (UTC-5/-4)
    eastern_sections = {
        'CT', 'DE', 'FL', 'WCF', 'NFL', 'SFL', 'GA', 'ME', 'MDC', 'MA', 'EMA', 'MI', 
        'NH', 'NJ', 'NNJ', 'SNJ', 'NY', 'NYC', 'LI', 'NLI', 'WNY', 'NC', 'OH', 
        'PA', 'EPA', 'WPA', 'RI', 'SC', 'VT', 'VA', 'WV'
    }
    
    # Alaska Time (UTC-9/-8)
    if section == 'AK':
        return 'America/Anchorage'
    
    # Hawaii Time (UTC-10)
    if section == 'HI':
        return 'Pacific/Honolulu'
    
    # Canadian sections - approximate by region
    canadian_sections = {
        'BC': 'America/Vancouver',      # Pacific
        'AB': 'America/Edmonton',       # Mountain  
        'SK': 'America/Regina',         # Central
        'MB': 'America/Winnipeg',       # Central
        'ON': 'America/Toronto',        # Eastern
        'QC': 'America/Montreal',       # Eastern
        'NB': 'America/Moncton',        # Atlantic
        'NS': 'America/Halifax',        # Atlantic
        'PE': 'America/Halifax',        # Atlantic
        'NL': 'America/St_Johns',       # Newfoundland
        'NT': 'America/Yellowknife',    # Mountain
        'NU': 'America/Iqaluit',        # Eastern
        'YT': 'America/Whitehorse'      # Pacific
    }
    
    if section in canadian_sections:
        return canadian_sections[section]
    
    # US sections by timezone
    if section in pacific_sections:
        return 'America/Los_Angeles'
    elif section in mountain_sections:
        return 'America/Denver'
    elif section in central_sections:
        return 'America/Chicago'
    elif section in eastern_sections:
        return 'America/New_York'
    else:
        # Default for international sections (MX, DX, etc.)
        return 'UTC'

class StationSetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setup_name = db.Column(db.String(100), nullable=False, default='Default Setup')
    station_callsign = db.Column(db.String(20), nullable=False)
    operator_name = db.Column(db.String(100), nullable=False)
    operator_callsign = db.Column(db.String(20), nullable=False)
    wfd_category = db.Column(db.String(10), nullable=False)
    arrl_section = db.Column(db.String(10), nullable=False)
    timezone = db.Column(db.String(50), nullable=True)
    power_level = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=True)
    grid_square = db.Column(db.String(10), nullable=True)
    additional_operators = db.Column(db.Text, nullable=True)
    equipment_notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class WFDObjective(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    multiplier = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    completion_notes = db.Column(db.Text, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    callsign = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)
    mode = db.Column(db.String(10), nullable=False)
    rst_sent = db.Column(db.String(10), nullable=False)
    rst_received = db.Column(db.String(10), nullable=False)
    exchange_sent = db.Column(db.String(50), nullable=False)
    exchange_received = db.Column(db.String(50), nullable=False)
    arrl_section = db.Column(db.String(10), nullable=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)
    operator_callsign = db.Column(db.String(20), nullable=True)  # Which operator made this contact
    station_setup_id = db.Column(db.Integer, db.ForeignKey('station_setup.id'), nullable=True)  # Which setup was active

def validate_exchange(form, field):
    """Custom validator for Winter Field Day exchange format"""
    is_valid, error_message = validate_wfd_exchange(field.data)
    if not is_valid:
        raise ValidationError(error_message)

class StationSetupForm(FlaskForm):
    setup_name = StringField('Setup Name', validators=[DataRequired(), Length(min=2, max=100)], default='Default Setup')
    station_callsign = StringField('Station Callsign', validators=[DataRequired(), Length(min=3, max=20)])
    operator_name = StringField('Primary Operator Name', validators=[DataRequired(), Length(min=2, max=100)])
    operator_callsign = StringField('Primary Operator Callsign', validators=[DataRequired(), Length(min=3, max=20)])
    wfd_category = SelectField('WFD Category', choices=[
        ('1H', '1H - Single transmitter, Home station'),
        ('2H', '2H - Two transmitters, Home station'),
        ('3H', '3H - Three transmitters, Home station'),
        ('4H', '4H - Four transmitters, Home station'),
        ('5H', '5H - Five transmitters, Home station'),
        ('1I', '1I - Single transmitter, Indoor station'),
        ('2I', '2I - Two transmitters, Indoor station'),
        ('3I', '3I - Three transmitters, Indoor station'),
        ('4I', '4I - Four transmitters, Indoor station'),
        ('5I', '5I - Five transmitters, Indoor station'),
        ('1O', '1O - Single transmitter, Outdoor station'),
        ('2O', '2O - Two transmitters, Outdoor station'),
        ('3O', '3O - Three transmitters, Outdoor station'),
        ('4O', '4O - Four transmitters, Outdoor station'),
        ('5O', '5O - Five transmitters, Outdoor station'),
        ('1M', '1M - Single transmitter, Mobile station'),
        ('2M', '2M - Two transmitters, Mobile station'),
        ('3M', '3M - Three transmitters, Mobile station'),
        ('4M', '4M - Four transmitters, Mobile station'),
        ('5M', '5M - Five transmitters, Mobile station')
    ], validators=[DataRequired()])
    arrl_section = SelectField('ARRL Section', choices=[
        ('', 'Select Your Section'),
        ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('EB', 'East Bay'), ('LAX', 'Los Angeles'), ('ORG', 'Orange'), 
        ('SB', 'Santa Barbara'), ('SCV', 'Santa Clara Valley'), ('SF', 'San Francisco'), 
        ('SJV', 'San Joaquin Valley'), ('SV', 'Sacramento Valley'), ('PAC', 'Pacific'),
        ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), 
        ('FL', 'Florida'), ('WCF', 'West Central Florida'), ('NFL', 'Northern Florida'), ('SFL', 'Southern Florida'),
        ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'),
        ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'),
        ('LA', 'Louisiana'), ('ME', 'Maine'), ('MDC', 'Maryland-DC'), 
        ('MA', 'Western Massachusetts'), ('EMA', 'Eastern Massachusetts'), ('MI', 'Michigan'), 
        ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), 
        ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), 
        ('NJ', 'New Jersey'), ('NNJ', 'Northern New Jersey'), ('SNJ', 'Southern New Jersey'), 
        ('NM', 'New Mexico'), ('NY', 'New York'), ('NYC', 'New York City'), ('LI', 'Long Island'), 
        ('NLI', 'Northern New York'), ('WNY', 'Western New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
        ('OK', 'Oklahoma'), ('OR', 'Oregon'), 
        ('PA', 'Pennsylvania'), ('EPA', 'Eastern Pennsylvania'), ('WPA', 'Western Pennsylvania'),
        ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), 
        ('TX', 'Texas'), ('NTX', 'North Texas'), ('STX', 'South Texas'), ('WTX', 'West Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), 
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
        ('AB', 'Alberta'), ('BC', 'British Columbia'), ('MB', 'Manitoba'),
        ('NB', 'New Brunswick'), ('NL', 'Newfoundland/Labrador'), ('NT', 'Northwest Territories'), 
        ('NS', 'Nova Scotia'), ('NU', 'Nunavut'), ('ON', 'Ontario'), ('PE', 'Prince Edward Island'), 
        ('QC', 'Quebec'), ('SK', 'Saskatchewan'), ('YT', 'Yukon')
    ], validators=[DataRequired()])
    timezone = SelectField('Timezone Override (Optional)', choices=[
        ('', 'Auto-detect from ARRL Section'),
        ('America/Los_Angeles', 'Pacific Time'),
        ('America/Denver', 'Mountain Time'),
        ('America/Chicago', 'Central Time'),
        ('America/New_York', 'Eastern Time'),
        ('America/Anchorage', 'Alaska Time'),
        ('Pacific/Honolulu', 'Hawaii Time'),
        ('America/Vancouver', 'Pacific (Vancouver)'),
        ('America/Edmonton', 'Mountain (Edmonton)'),
        ('America/Regina', 'Central (Regina)'),
        ('America/Winnipeg', 'Central (Winnipeg)'),
        ('America/Toronto', 'Eastern (Toronto)'),
        ('America/Montreal', 'Eastern (Montreal)'),
        ('America/Moncton', 'Atlantic (Moncton)'),
        ('America/Halifax', 'Atlantic (Halifax)'),
        ('America/St_Johns', 'Newfoundland'),
        ('UTC', 'UTC')
    ])
    power_level = StringField('Power Level (Watts)', validators=[DataRequired()], default='100')
    location = StringField('Operating Location', validators=[Length(max=200)])
    grid_square = StringField('Grid Square', validators=[Length(max=10)])
    additional_operators = TextAreaField('Additional Operators')
    equipment_notes = TextAreaField('Equipment/Antenna Notes')
    submit = SubmitField('Save Station Setup')

class ContactForm(FlaskForm):
    callsign = StringField('Callsign', validators=[DataRequired(), Length(min=3, max=20)])
    frequency = StringField('Frequency (MHz)', validators=[DataRequired()])
    mode = SelectField('Mode', choices=[
        ('SSB', 'SSB'),
        ('CW', 'CW'),
        ('FT8', 'FT8'),
        ('FT4', 'FT4'),
        ('PSK31', 'PSK31'),
        ('RTTY', 'RTTY'),
        ('FM', 'FM')
    ], validators=[DataRequired()])
    rst_sent = StringField('RST Sent', validators=[DataRequired()], default='599')
    rst_received = StringField('RST Received', validators=[DataRequired()], default='599')
    exchange_sent = StringField('Exchange Sent', validators=[DataRequired(), validate_exchange])
    exchange_received = StringField('Exchange Received', validators=[DataRequired(), validate_exchange])
    operator_callsign = SelectField('Operator', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    submit = SubmitField('Log Contact')

@app.route('/')
def home():
    recent_contacts = Contact.query.order_by(Contact.datetime.desc()).limit(10).all()
    total_contacts = Contact.query.count()
    station_info = get_active_station()
    
    # Calculate score for home page display
    score_data = calculate_wfd_score()
    
    return render_template('index.html', contacts=recent_contacts, total=total_contacts, station_info=station_info, score_data=score_data)

@app.route('/log', methods=['GET', 'POST'])
def log_contact():
    form = ContactForm()
    station_info = get_active_station()
    
    # Populate operator choices
    operators = get_available_operators()
    form.operator_callsign.choices = operators
    
    # Auto-populate exchange sent field and default operator on GET request
    if request.method == 'GET' and station_info:
        form.exchange_sent.data = f"{station_info.wfd_category} {station_info.arrl_section}"
        # Default to primary operator
        if operators:
            form.operator_callsign.data = operators[0][0]
    
    if form.validate_on_submit():
        # Extract ARRL section from exchange received
        arrl_section = extract_arrl_section(form.exchange_received.data)
        
        contact = Contact(
            callsign=form.callsign.data.upper(),
            frequency=form.frequency.data,
            mode=form.mode.data,
            rst_sent=form.rst_sent.data,
            rst_received=form.rst_received.data,
            exchange_sent=form.exchange_sent.data,
            exchange_received=form.exchange_received.data,
            arrl_section=arrl_section,
            notes=form.notes.data,
            operator_callsign=form.operator_callsign.data,
            station_setup_id=station_info.id if station_info else None
        )
        db.session.add(contact)
        db.session.commit()
        flash(f'Contact with {form.callsign.data.upper()} logged successfully!', 'success')
        return redirect(url_for('log_contact'))
    
    return render_template('log.html', form=form, station_info=station_info)

@app.route('/contacts')
def contacts():
    page = request.args.get('page', 1, type=int)
    contacts = Contact.query.order_by(Contact.datetime.desc()).paginate(
        page=page, per_page=20, error_out=False)
    return render_template('contacts.html', contacts=contacts)





def get_active_station():
    """Get the currently active station setup"""
    return StationSetup.query.filter_by(is_active=True).first()

def get_available_operators():
    """Get list of available operators from active station setup"""
    active_station = get_active_station()
    if not active_station:
        return []
    
    operators = [(active_station.operator_callsign, f"{active_station.operator_name} ({active_station.operator_callsign})")]
    
    # Add additional operators if any
    if active_station.additional_operators:
        additional_ops = active_station.additional_operators.strip().split('\n')
        for op in additional_ops:
            op = op.strip()
            if op and op != active_station.operator_callsign:
                # Try to extract callsign if in "Name (CALL)" format
                if '(' in op and ')' in op:
                    call = op.split('(')[1].split(')')[0].upper()
                    operators.append((call, op))
                else:
                    # Assume it's just a callsign
                    operators.append((op.upper(), op.upper()))
    
    return operators

def set_active_station(station_id):
    """Set a station as active and deactivate all others"""
    # Deactivate all stations
    StationSetup.query.update({'is_active': False})
    
    # Activate the selected station
    station = StationSetup.query.get(station_id)
    if station:
        station.is_active = True
        db.session.commit()
        return True
    return False

def check_duplicate_contact(callsign, frequency, mode):
    """Check for potential duplicate contacts"""
    # Look for existing contacts with same callsign on same band/mode within last 10 minutes
    ten_minutes_ago = datetime.utcnow() - timedelta(minutes=10)
    
    # Extract band from frequency for comparison
    try:
        freq_float = float(frequency)
        # Define band ranges (simplified)
        if 1.8 <= freq_float <= 2.0:
            band = '160m'
        elif 3.5 <= freq_float <= 4.0:
            band = '80m'
        elif 7.0 <= freq_float <= 7.3:
            band = '40m'
        elif 14.0 <= freq_float <= 14.35:
            band = '20m'
        elif 21.0 <= freq_float <= 21.45:
            band = '15m'
        elif 28.0 <= freq_float <= 29.7:
            band = '10m'
        elif 50.0 <= freq_float <= 54.0:
            band = '6m'
        elif 144.0 <= freq_float <= 148.0:
            band = '2m'
        elif 420.0 <= freq_float <= 450.0:
            band = '70cm'
        else:
            band = f"{freq_float}MHz"
    except:
        band = frequency
    
    # Check for exact callsign match (possible dupe)
    exact_dupe = Contact.query.filter(
        Contact.callsign.ilike(callsign),
        Contact.datetime >= ten_minutes_ago
    ).first()
    
    # Check for same callsign on same band (band/mode dupe)
    band_dupe = None
    existing_contacts = Contact.query.filter(
        Contact.callsign.ilike(callsign)
    ).all()
    
    for contact in existing_contacts:
        try:
            existing_freq = float(contact.frequency)
            existing_band = band  # Same logic as above - simplified for brevity
            if existing_band == band and contact.mode.upper() == mode.upper():
                band_dupe = contact
                break
        except:
            continue
    
    return {
        'exact_dupe': exact_dupe,
        'band_dupe': band_dupe,
        'is_duplicate': exact_dupe is not None,
        'is_band_duplicate': band_dupe is not None
    }

def get_band_from_frequency(frequency):
    """Convert frequency to band name"""
    try:
        freq = float(frequency)
        if 1.8 <= freq <= 2.0:
            return '160m'
        elif 3.5 <= freq <= 4.0:
            return '80m'
        elif 5.3 <= freq <= 5.4:
            return '60m'
        elif 7.0 <= freq <= 7.3:
            return '40m'
        elif 10.1 <= freq <= 10.15:
            return '30m'
        elif 14.0 <= freq <= 14.35:
            return '20m'
        elif 18.068 <= freq <= 18.168:
            return '17m'
        elif 21.0 <= freq <= 21.45:
            return '15m'
        elif 24.89 <= freq <= 24.99:
            return '12m'
        elif 28.0 <= freq <= 29.7:
            return '10m'
        elif 50.0 <= freq <= 54.0:
            return '6m'
        elif 144.0 <= freq <= 148.0:
            return '2m'
        elif 219.0 <= freq <= 225.0:
            return '1.25m'
        elif 420.0 <= freq <= 450.0:
            return '70cm'
        elif 902.0 <= freq <= 928.0:
            return '33cm'
        elif 1240.0 <= freq <= 1300.0:
            return '23cm'
        else:
            return f"{freq}MHz"
    except (ValueError, TypeError):
        return str(frequency)

def get_band_activity_data():
    """Get comprehensive band activity statistics"""
    try:
        contacts = Contact.query.all()
        
        # Band statistics
        band_counts = {}
        band_modes = {}
        band_hourly = {}
        
        for contact in contacts:
            try:
                band = get_band_from_frequency(contact.frequency)
                mode = contact.mode.upper() if contact.mode else 'UNKNOWN'
                hour = contact.datetime.hour if contact.datetime else 0
                
                # Count contacts per band
                band_counts[band] = band_counts.get(band, 0) + 1
                
                # Track modes per band
                if band not in band_modes:
                    band_modes[band] = {}
                band_modes[band][mode] = band_modes[band].get(mode, 0) + 1
                
                # Track hourly activity per band
                if band not in band_hourly:
                    band_hourly[band] = {h: 0 for h in range(24)}
                band_hourly[band][hour] += 1
            except Exception:
                # Skip problematic contacts
                continue
        
        return {
            'band_counts': band_counts or {},
            'modes_per_band': band_modes or {},
            'hourly_activity': band_hourly or {}
        }
    except Exception:
        # Return empty data if there's a major error
        return {
            'band_counts': {},
            'modes_per_band': {},
            'hourly_activity': {}
        }

def get_temporal_activity_data():
    """Get time-based activity statistics"""
    try:
        contacts = Contact.query.order_by(Contact.datetime).all()
        
        # Hourly activity (24-hour format)
        hourly_counts = {h: 0 for h in range(24)}
        
        # Daily activity
        daily_counts = {}
        
        # Cumulative contacts over time
        cumulative_data = []
        cumulative_count = 0
        
        for contact in contacts:
            try:
                if contact.datetime:
                    # Hourly statistics
                    hourly_counts[contact.datetime.hour] += 1
                    
                    # Daily statistics
                    date_str = contact.datetime.strftime('%Y-%m-%d')
                    daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
                    
                    # Cumulative statistics
                    cumulative_count += 1
                    cumulative_data.append({
                        'time': contact.datetime.strftime('%Y-%m-%d %H:%M'),
                        'count': cumulative_count
                    })
            except Exception:
                # Skip problematic contacts
                continue
        
        return {
            'hourly_counts': hourly_counts,
            'daily_counts': daily_counts,
            'cumulative_data': cumulative_data
        }
    except Exception:
        # Return empty data if there's a major error
        return {
            'hourly_counts': {h: 0 for h in range(24)},
            'daily_counts': {},
            'cumulative_data': []
        }

def get_mode_statistics():
    """Get detailed mode statistics"""
    try:
        contacts = Contact.query.all()
        
        mode_counts = {}
        mode_points = {}
        mode_hourly = {}
        
        for contact in contacts:
            try:
                mode = contact.mode.upper() if contact.mode else 'UNKNOWN'
                hour = contact.datetime.hour if contact.datetime else 0
                
                # Count contacts per mode
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
                
                # Calculate points per mode (CW/Digital = 2, Voice = 1)
                points = 2 if mode in ['CW', 'RTTY', 'PSK31', 'FT8', 'FT4', 'JS8', 'MSK144'] else 1
                mode_points[mode] = mode_points.get(mode, 0) + points
                
                # Track hourly activity per mode
                if mode not in mode_hourly:
                    mode_hourly[mode] = {h: 0 for h in range(24)}
                mode_hourly[mode][hour] += 1
            except Exception:
                # Skip problematic contacts
                continue
        
        return {
            'mode_counts': mode_counts or {},
            'mode_points': mode_points or {},
            'mode_hourly': mode_hourly or {}
        }
    except Exception:
        # Return empty data if there's a major error
        return {
            'mode_counts': {},
            'mode_points': {},
            'mode_hourly': {}
        }

def calculate_wfd_score():
    """Calculate Winter Field Day score including contact points, multipliers, and objective bonuses"""
    # Get all contacts
    contacts = Contact.query.all()
    
    # Calculate contact points
    contact_points = 0
    for contact in contacts:
        if contact.mode.upper() in ['CW', 'RTTY', 'PSK', 'FT8', 'FT4', 'JS8', 'MSK144', 'DATA']:
            contact_points += 2  # CW/Digital = 2 points
        else:
            contact_points += 1  # Phone = 1 point
    
    # Calculate multipliers (unique sections/countries worked)
    unique_sections = set()
    for contact in contacts:
        if contact.arrl_section:
            unique_sections.add(contact.arrl_section.upper())
    
    multipliers = len(unique_sections)
    if multipliers == 0:
        multipliers = 1  # Minimum multiplier of 1
    
    # Calculate base score
    base_score = contact_points * multipliers
    
    # Calculate objective multipliers
    completed_objectives = WFDObjective.query.filter_by(completed=True).all()
    objective_multiplier = sum(obj.multiplier for obj in completed_objectives)
    
    # Final score calculation
    final_score = base_score * (1 + objective_multiplier)
    
    return {
        'contact_points': contact_points,
        'multipliers': multipliers,
        'unique_sections': sorted(list(unique_sections)),
        'base_score': base_score,
        'objective_multiplier': objective_multiplier,
        'completed_objectives_count': len(completed_objectives),
        'final_score': int(final_score)
    }

@app.route('/stats')
def stats():
    total_contacts = Contact.query.count()
    modes = db.session.query(Contact.mode, db.func.count(Contact.id)).group_by(Contact.mode).all()
    bands = db.session.query(Contact.frequency, db.func.count(Contact.id)).group_by(Contact.frequency).all()
    operators = db.session.query(Contact.operator_callsign, db.func.count(Contact.id)).filter(
        Contact.operator_callsign != None
    ).group_by(Contact.operator_callsign).all()
    station_info = get_active_station()
    
    # Calculate WFD score
    score_data = calculate_wfd_score()
    
    # Get advanced analytics data
    band_activity = get_band_activity_data()
    temporal_activity = get_temporal_activity_data()
    mode_statistics = get_mode_statistics()
    
    return render_template('stats.html', 
                         total=total_contacts, 
                         modes=modes, 
                         bands=bands, 
                         operators=operators,
                         station_info=station_info,
                         score_data=score_data,
                         band_activity=band_activity,
                         temporal_activity=temporal_activity,
                         mode_statistics=mode_statistics)

def section_to_state(section):
    """Map ARRL sections to US state abbreviations"""
    section_map = {
        'AL': 'AL', 'AK': 'AK', 'AZ': 'AZ', 'AR': 'AR',
        'EB': 'CA', 'LAX': 'CA', 'ORG': 'CA', 'SB': 'CA', 'SCV': 'CA', 'SF': 'CA', 'SJV': 'CA', 'SV': 'CA', 'PAC': 'CA',
        'CO': 'CO', 'CT': 'CT', 'DE': 'DE',
        'WCF': 'FL', 'NFL': 'FL', 'SFL': 'FL',
        'GA': 'GA', 'HI': 'HI', 'ID': 'ID', 'IL': 'IL', 'IN': 'IN', 'IA': 'IA', 'KS': 'KS', 'KY': 'KY',
        'LA': 'LA', 'ME': 'ME', 'MDC': 'MD', 'MA': 'MA', 'EMA': 'MA', 'MI': 'MI', 'MN': 'MN',
        'MS': 'MS', 'MO': 'MO', 'MT': 'MT', 'NE': 'NE', 'NV': 'NV', 'NH': 'NH',
        'NNJ': 'NJ', 'SNJ': 'NJ', 'NM': 'NM',
        'NYC': 'NY', 'LI': 'NY', 'NLI': 'NY', 'WNY': 'NY',
        'NC': 'NC', 'ND': 'ND', 'OH': 'OH', 'OK': 'OK', 'OR': 'OR',
        'EPA': 'PA', 'WPA': 'PA',
        'RI': 'RI', 'SC': 'SC', 'SD': 'SD', 'TN': 'TN',
        'NTX': 'TX', 'STX': 'TX', 'WTX': 'TX',
        'UT': 'UT', 'VT': 'VT', 'VA': 'VA', 'WA': 'WA', 'WV': 'WV', 'WI': 'WI', 'WY': 'WY'
    }
    return section_map.get(section, None)

def convert_frequency_to_band(frequency_str):
    """Convert frequency in MHz to band designation for Cabrillo"""
    try:
        freq_mhz = float(frequency_str)
        
        # HF bands - use frequency in kHz
        if 1.8 <= freq_mhz <= 2.0:
            return str(int(freq_mhz * 1000))  # 160m
        elif 3.5 <= freq_mhz <= 4.0:
            return str(int(freq_mhz * 1000))  # 80m
        elif 7.0 <= freq_mhz <= 7.3:
            return str(int(freq_mhz * 1000))  # 40m
        elif 14.0 <= freq_mhz <= 14.35:
            return str(int(freq_mhz * 1000))  # 20m
        elif 21.0 <= freq_mhz <= 21.45:
            return str(int(freq_mhz * 1000))  # 15m
        elif 28.0 <= freq_mhz <= 29.7:
            return str(int(freq_mhz * 1000))  # 10m
        # VHF/UHF bands - use band designation
        elif 50.0 <= freq_mhz <= 54.0:
            return "50"
        elif 144.0 <= freq_mhz <= 148.0:
            return "144"
        elif 220.0 <= freq_mhz <= 225.0:
            return "222"
        elif 420.0 <= freq_mhz <= 450.0:
            return "432"
        elif 902.0 <= freq_mhz <= 928.0:
            return "902"
        elif 1240.0 <= freq_mhz <= 1300.0:
            return "1.2G"
        elif 2300.0 <= freq_mhz <= 2450.0:
            return "2.3G"
        elif 3300.0 <= freq_mhz <= 3500.0:
            return "3.4G"
        elif 5650.0 <= freq_mhz <= 5925.0:
            return "5.7G"
        elif 10000.0 <= freq_mhz <= 10500.0:
            return "10G"
        elif 24000.0 <= freq_mhz <= 24250.0:
            return "24G"
        else:
            return str(int(freq_mhz * 1000))  # Default to kHz
    except:
        return "14000"  # Default frequency

def convert_mode_for_cabrillo(mode):
    """Convert mode to Cabrillo format"""
    mode_upper = mode.upper()
    if mode_upper == 'CW':
        return 'CW'
    elif mode_upper in ['SSB', 'AM', 'FM', 'DMR', 'C4FM']:
        return 'PH'
    else:
        return 'DG'  # Digital

def generate_cabrillo_log():
    """Generate Cabrillo format log for WFD submission"""
    contacts = Contact.query.order_by(Contact.datetime).all()
    station_info = get_active_station()
    
    if not station_info:
        return None
    
    # Build Cabrillo header
    lines = []
    lines.append("START-OF-LOG: 3.0")
    lines.append(f"LOCATION: {station_info.arrl_section}")
    lines.append(f"CALLSIGN: {station_info.station_callsign}")
    lines.append("CONTEST: WFD")
    lines.append("CATEGORY-OPERATOR: SINGLE-OP")
    lines.append("CATEGORY-ASSISTED: NON-ASSISTED")
    lines.append("CATEGORY-BAND: ALL")
    lines.append("CATEGORY-MODE: MIXED")
    lines.append("CATEGORY-POWER: LOW")
    lines.append("CATEGORY-STATION: FIXED")
    lines.append("CATEGORY-TRANSMITTER: ONE")
    lines.append(f"CLAIMED-SCORE: {len(contacts)}")
    lines.append(f"OPERATORS: {station_info.operator_callsign}")
    lines.append(f"NAME: {station_info.operator_name}")
    lines.append("ADDRESS: ")
    lines.append("ADDRESS-CITY: ")
    lines.append("ADDRESS-STATE: ")
    lines.append("ADDRESS-POSTALCODE: ")
    lines.append("ADDRESS-COUNTRY: ")
    lines.append(f"X-EXCHANGE: {station_info.wfd_category}")
    lines.append("SOAPBOX: Generated by WFD Logger")
    lines.append("EMAIL: ")
    
    # Add QSO lines
    for contact in contacts:
        freq = convert_frequency_to_band(contact.frequency)
        mode = convert_mode_for_cabrillo(contact.mode)
        date_str = contact.datetime.strftime('%Y-%m-%d')
        time_str = contact.datetime.strftime('%H%M')
        
        qso_line = f"QSO: {freq:>5} {mode:>2} {date_str} {time_str} {station_info.station_callsign} {station_info.wfd_category} {station_info.arrl_section} {contact.callsign} {contact.exchange_received}"
        lines.append(qso_line)
    
    lines.append("END-OF-LOG: ")
    
    return '\n'.join(lines)

def generate_adif_log():
    """Generate ADIF format log"""
    contacts = Contact.query.order_by(Contact.datetime).all()
    station_info = get_active_station()
    
    lines = []
    lines.append("ADIF Export from WFD Logger")
    lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    lines.append("")
    lines.append("<ADIF_VER:5>3.1.4")
    lines.append("<PROGRAMID:10>WFD Logger")
    lines.append("<EOH>")
    lines.append("")
    
    for contact in contacts:
        # Convert frequency to MHz format for ADIF
        try:
            freq_mhz = float(contact.frequency)
        except:
            freq_mhz = 14.205  # Default
            
        # Date and time in ADIF format
        qso_date = contact.datetime.strftime('%Y%m%d')
        time_on = contact.datetime.strftime('%H%M%S')
        
        # Build ADIF record
        record_parts = []
        record_parts.append(f"<CALL:{len(contact.callsign)}>{contact.callsign}")
        record_parts.append(f"<QSO_DATE:8>{qso_date}")
        record_parts.append(f"<TIME_ON:6>{time_on}")
        record_parts.append(f"<FREQ:{len(contact.frequency)}>{contact.frequency}")
        record_parts.append(f"<MODE:{len(contact.mode)}>{contact.mode}")
        record_parts.append(f"<RST_SENT:{len(contact.rst_sent)}>{contact.rst_sent}")
        record_parts.append(f"<RST_RCVD:{len(contact.rst_received)}>{contact.rst_received}")
        
        if contact.exchange_received:
            record_parts.append(f"<STX_STRING:{len(contact.exchange_sent)}>{contact.exchange_sent}")
            record_parts.append(f"<SRX_STRING:{len(contact.exchange_received)}>{contact.exchange_received}")
        
        if contact.arrl_section:
            record_parts.append(f"<STATE:{len(contact.arrl_section)}>{contact.arrl_section}")
            
        if contact.notes:
            record_parts.append(f"<NOTES:{len(contact.notes)}>{contact.notes}")
            
        # Add contest information
        record_parts.append("<CONTEST_ID:3>WFD")
        
        if station_info:
            if station_info.grid_square:
                record_parts.append(f"<GRIDSQUARE:{len(station_info.grid_square)}>{station_info.grid_square}")
        
        record_parts.append("<EOR>")
        lines.append(''.join(record_parts))
    
    return '\n'.join(lines)

def initialize_wfd_objectives():
    """Initialize WFD 2026 objectives if they don't exist"""
    if WFDObjective.query.count() == 0:
        objectives = [
            ("Alternative Power", "Operate exclusively on alternative power (batteries, solar, etc.)", 1),
            ("Away from Home", "Set up your station more than 0.5 miles from your home", 3),
            ("Multiple Antennas", "Deploy two or more antennas and make at least one contact on each", 1),
            ("FM Satellite Contact", "Make at least 1 FM satellite contact", 2),
            ("SSB/CW Satellite Contact", "Make at least one SSB or CW satellite contact", 3),
            ("Winlink Email", "Send and receive at least one Winlink email via RF", 1),
            ("WFD Special Bulletin", "Copy the Winter Field Day special bulletin message", 1),
            ("Six Different Bands", "Make three contacts on at least six different bands", 6),
            ("Twelve Different Bands", "Make three contacts on at least twelve different bands", 6),
            ("Multiple Modes", "Use multiple modes (Phone/CW/Digital)", 2),
            ("QRP Operation", "Operate with less than 10W phone or 5W CW/digital", 4),
            ("Six Continuous Hours", "Monitor and operate for six continuous hours", 2)
        ]
        
        for name, description, multiplier in objectives:
            objective = WFDObjective(name=name, description=description, multiplier=multiplier)
            db.session.add(objective)
        
        db.session.commit()

@app.route('/map')
def map_view():
    # Get unique ARRL sections worked
    sections = db.session.query(Contact.arrl_section).filter(Contact.arrl_section.isnot(None)).distinct().all()
    sections = [s[0] for s in sections if s[0]]
    
    # Convert sections to states
    states_worked = set()
    for section in sections:
        state = section_to_state(section)
        if state:
            states_worked.add(state)
    
    # Get section counts
    section_counts = db.session.query(Contact.arrl_section, db.func.count(Contact.id)).filter(
        Contact.arrl_section.isnot(None)).group_by(Contact.arrl_section).all()
    section_data = {section: count for section, count in section_counts if section}
    
    return render_template('map.html', 
                         states_worked=list(states_worked), 
                         sections_worked=sections,
                         section_data=section_data)

@app.route('/map-data')
def map_data():
    """API endpoint for map data"""
    sections = db.session.query(Contact.arrl_section).filter(Contact.arrl_section.isnot(None)).distinct().all()
    sections = [s[0] for s in sections if s[0]]
    
    states_worked = set()
    for section in sections:
        state = section_to_state(section)
        if state:
            states_worked.add(state)
    
    section_counts = db.session.query(Contact.arrl_section, db.func.count(Contact.id)).filter(
        Contact.arrl_section.isnot(None)).group_by(Contact.arrl_section).all()
    section_data = {section: count for section, count in section_counts if section}
    
    return jsonify({
        'states': list(states_worked),
        'sections': sections,
        'sectionCounts': section_data
    })

@app.route('/edit/<int:contact_id>', methods=['GET', 'POST'])
def edit_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    form = ContactForm()
    station_info = get_active_station()
    
    if form.validate_on_submit():
        # Extract ARRL section from exchange received (re-extract even if editing)
        arrl_section = extract_arrl_section(form.exchange_received.data)
        
        # Update contact with form data
        contact.callsign = form.callsign.data.upper()
        contact.frequency = form.frequency.data
        contact.mode = form.mode.data
        contact.rst_sent = form.rst_sent.data
        contact.rst_received = form.rst_received.data
        contact.exchange_sent = form.exchange_sent.data
        contact.exchange_received = form.exchange_received.data
        contact.arrl_section = arrl_section
        contact.notes = form.notes.data
        
        db.session.commit()
        flash(f'Contact with {contact.callsign} updated successfully!', 'success')
        return redirect(url_for('contacts'))
    
    # Pre-populate form with existing contact data
    elif request.method == 'GET':
        form.callsign.data = contact.callsign
        form.frequency.data = contact.frequency
        form.mode.data = contact.mode
        form.rst_sent.data = contact.rst_sent
        form.rst_received.data = contact.rst_received
        form.exchange_sent.data = contact.exchange_sent
        form.exchange_received.data = contact.exchange_received
        form.notes.data = contact.notes
    
    return render_template('edit.html', form=form, contact=contact, station_info=station_info)

@app.route('/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    callsign = contact.callsign
    
    db.session.delete(contact)
    db.session.commit()
    
    flash(f'Contact with {callsign} deleted successfully!', 'warning')
    return redirect(url_for('contacts'))

@app.route('/setup')
def station_setup():
    """Station setup management page - shows all setups"""
    all_setups = StationSetup.query.order_by(StationSetup.created_at.desc()).all()
    active_station = get_active_station()
    
    return render_template('setup.html', setups=all_setups, active_station=active_station)

@app.route('/setup/new', methods=['GET', 'POST'])
def new_station_setup():
    """Create a new station setup"""
    form = StationSetupForm()
    
    if form.validate_on_submit():
        # Create new setup
        new_setup = StationSetup(
            setup_name=form.setup_name.data,
            station_callsign=form.station_callsign.data.upper(),
            operator_name=form.operator_name.data,
            operator_callsign=form.operator_callsign.data.upper(),
            wfd_category=form.wfd_category.data,
            arrl_section=form.arrl_section.data,
            timezone=form.timezone.data if form.timezone.data else None,
            power_level=form.power_level.data,
            location=form.location.data,
            grid_square=form.grid_square.data.upper() if form.grid_square.data else None,
            additional_operators=form.additional_operators.data,
            equipment_notes=form.equipment_notes.data,
            is_active=False  # New setups are not automatically active
        )
        
        db.session.add(new_setup)
        db.session.commit()
        
        flash('Station setup created successfully!', 'success')
        return redirect(url_for('station_setup'))
    
    return render_template('setup_form.html', form=form, title='New Station Setup')

@app.route('/setup/edit/<int:setup_id>', methods=['GET', 'POST'])
def edit_station_setup(setup_id):
    """Edit an existing station setup"""
    setup = StationSetup.query.get_or_404(setup_id)
    form = StationSetupForm(obj=setup)
    
    if form.validate_on_submit():
        # Update existing setup
        setup.setup_name = form.setup_name.data
        setup.station_callsign = form.station_callsign.data.upper()
        setup.operator_name = form.operator_name.data
        setup.operator_callsign = form.operator_callsign.data.upper()
        setup.wfd_category = form.wfd_category.data
        setup.arrl_section = form.arrl_section.data
        setup.timezone = form.timezone.data if form.timezone.data else None
        setup.power_level = form.power_level.data
        setup.location = form.location.data
        setup.grid_square = form.grid_square.data.upper() if form.grid_square.data else None
        setup.additional_operators = form.additional_operators.data
        setup.equipment_notes = form.equipment_notes.data
        setup.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Station setup updated successfully!', 'success')
        return redirect(url_for('station_setup'))
    
    return render_template('setup_form.html', form=form, title=f'Edit {setup.setup_name}', setup=setup)

@app.route('/setup/activate/<int:setup_id>', methods=['POST'])
def activate_station_setup(setup_id):
    """Activate a station setup"""
    if set_active_station(setup_id):
        setup = StationSetup.query.get(setup_id)
        flash(f'Station setup "{setup.setup_name}" is now active!', 'success')
    else:
        flash('Failed to activate station setup.', 'error')
    
    return redirect(url_for('station_setup'))

@app.route('/setup/delete/<int:setup_id>', methods=['POST'])
def delete_station_setup(setup_id):
    """Delete a station setup"""
    setup = StationSetup.query.get_or_404(setup_id)
    
    # Don't allow deleting the active setup
    if setup.is_active:
        flash('Cannot delete the active station setup. Please activate a different setup first.', 'error')
        return redirect(url_for('station_setup'))
    
    setup_name = setup.setup_name
    db.session.delete(setup)
    db.session.commit()
    
    flash(f'Station setup "{setup_name}" deleted successfully!', 'success')
    return redirect(url_for('station_setup'))

@app.route('/rules')
def wfd_rules():
    return render_template('rules.html')

@app.route('/check_duplicate')
def check_duplicate():
    """API endpoint to check for duplicate contacts"""
    callsign = request.args.get('callsign', '').upper()
    frequency = request.args.get('frequency', '')
    mode = request.args.get('mode', '')
    
    if not callsign or not frequency or not mode:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    dupe_check = check_duplicate_contact(callsign, frequency, mode)
    
    response_data = {
        'is_duplicate': dupe_check['is_duplicate'],
        'is_band_duplicate': dupe_check['is_band_duplicate'],
        'warnings': []
    }
    
    if dupe_check['exact_dupe']:
        response_data['warnings'].append({
            'type': 'danger',
            'message': f"Possible duplicate: {callsign} worked recently at {dupe_check['exact_dupe'].datetime.strftime('%H:%M UTC')}"
        })
    
    if dupe_check['band_dupe'] and not dupe_check['exact_dupe']:
        response_data['warnings'].append({
            'type': 'warning', 
            'message': f"Already worked {callsign} on this band/mode at {dupe_check['band_dupe'].datetime.strftime('%H:%M UTC')}"
        })
    
    return jsonify(response_data)


@app.route('/objectives', methods=['GET', 'POST'])
def objectives():
    """View and update WFD objectives"""
    # Initialize objectives if they don't exist
    initialize_wfd_objectives()
    
    if request.method == 'POST':
        # Handle objective completion updates
        for objective in WFDObjective.query.all():
            completed = request.form.get(f'objective_{objective.id}') is not None
            notes = request.form.get(f'notes_{objective.id}', '').strip()
            
            if completed != objective.completed:
                objective.completed = completed
                objective.completed_at = datetime.utcnow() if completed else None
                
            if notes != (objective.completion_notes or ''):
                objective.completion_notes = notes if notes else None
        
        db.session.commit()
        flash('Objectives updated successfully!', 'success')
        return redirect(url_for('objectives'))
    
    objectives = WFDObjective.query.all()
    total_multiplier = sum(obj.multiplier for obj in objectives if obj.completed)
    
    return render_template('objectives.html', objectives=objectives, total_multiplier=total_multiplier)

@app.route('/download/cabrillo')
def download_cabrillo():
    """Download Cabrillo format log"""
    station_info = get_active_station()
    if not station_info:
        flash('Station setup required to generate log files.', 'error')
        return redirect(url_for('station_setup'))
    
    cabrillo_content = generate_cabrillo_log()
    if not cabrillo_content:
        flash('Unable to generate Cabrillo log. Please check your station setup.', 'error')
        return redirect(url_for('contacts'))
    
    filename = f"{station_info.station_callsign}_WFD_2026.log"
    
    return Response(
        cabrillo_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@app.route('/download/adif')
def download_adif():
    """Download ADIF format log"""
    station_info = get_active_station()
    
    adif_content = generate_adif_log()
    
    filename = f"{station_info.station_callsign if station_info else 'WFD'}_contacts.adif"
    
    return Response(
        adif_content,
        mimetype='text/plain',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@app.route('/api/station_timezone')
def station_timezone():
    """Get the timezone information for the active station"""
    station_info = get_active_station()
    
    if not station_info:
        return jsonify({
            'timezone': 'America/New_York',
            'arrl_section': None,
            'label': 'Eastern'
        })
    
    # Get timezone from station or derive from ARRL section
    if hasattr(station_info, 'timezone') and station_info.timezone:
        timezone_name = station_info.timezone
    else:
        timezone_name = get_arrl_section_timezone(station_info.arrl_section)
    
    # Generate a friendly label
    timezone_labels = {
        'America/Los_Angeles': 'Pacific',
        'America/Denver': 'Mountain', 
        'America/Chicago': 'Central',
        'America/New_York': 'Eastern',
        'America/Anchorage': 'Alaska',
        'Pacific/Honolulu': 'Hawaii',
        'America/Vancouver': 'Pacific',
        'America/Edmonton': 'Mountain',
        'America/Regina': 'Central',
        'America/Winnipeg': 'Central', 
        'America/Toronto': 'Eastern',
        'America/Montreal': 'Eastern',
        'America/Moncton': 'Atlantic',
        'America/Halifax': 'Atlantic',
        'America/St_Johns': 'Newfoundland',
        'UTC': 'UTC'
    }
    
    label = timezone_labels.get(timezone_name, 'Local')
    
    return jsonify({
        'timezone': timezone_name,
        'arrl_section': station_info.arrl_section,
        'label': label
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)