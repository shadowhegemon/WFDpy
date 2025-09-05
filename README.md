# WFDpy - Winter Field Day Logger

A comprehensive web-based logging application for Winter Field Day contest operations, built with Flask and designed for amateur radio operators.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

WFDpy is a full-featured contest logging application specifically designed for Winter Field Day operations. It provides real-time logging, scoring, statistics, and export functionality in a modern, responsive web interface.

For more information about Winter Field Day, visit the official website: [https://winterfieldday.org](https://winterfieldday.org/index.php#hero)

## ✨ Features

### Core Logging Functionality
- **Real-time Contact Logging** - Log QSOs with comprehensive validation
- **Exchange Validation** - Automatic validation of Winter Field Day exchange format
- **Duplicate Detection** - Real-time warnings for potential duplicate contacts
- **Contact Management** - Edit, delete, and manage logged contacts
- **Export Capabilities** - Generate Cabrillo (.log) and ADIF (.adif) files

### Contest Integration
- **Real-time Contest Clock** - Live countdown and status display
- **Automatic Scoring** - Calculate points with WFD multipliers and bonuses
- **WFD Objectives Tracking** - Monitor progress on bonus objectives
- **Band/Mode Statistics** - Comprehensive activity analysis

### Station Management
- **Multi-Station Support** - Configure multiple station setups
- **Operator Management** - Track multiple operators per station
- **Active Station Selection** - Switch between configured stations
- **Exchange Auto-population** - Automatic exchange generation from setup

### Advanced Features
- **Comprehensive Theme System** - 26 themes including school colors, military, and seasonal options
- **Keyboard Shortcuts System** - Rapid logging shortcuts for power users and contest operations
- **Real-time Clock Display** - GMT and local time based on station's ARRL section timezone
- **Timezone Auto-detection** - Automatic timezone mapping from ARRL sections with manual override
- **Band Activity Charts** - Visual analytics with Chart.js
- **Responsive Design** - Mobile-friendly interface
- **Contest Status Clock** - UTC time display with contest countdown and status

### Technical Features
- **Modern Web Stack** - Flask, SQLAlchemy, Bootstrap 5
- **Database Management** - SQLite with automatic schema management
- **Input Validation** - Comprehensive form validation and sanitization
- **Error Handling** - Graceful error recovery and user feedback
- **Test Coverage** - Comprehensive unit test suite

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shadowhegemon/WFDpy.git
   cd WFDpy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to `http://localhost:5000`
   - Start logging contacts!

### First Time Setup
1. Visit the **Station Setup** page to configure your station
2. Enter your callsign, contest class, and ARRL section
3. Add operators if running multi-operator
4. Start logging contacts from the **Log Contact** page

## 📋 Usage Guide

### Logging Contacts
1. Navigate to **Log Contact** from the main menu
2. Enter the contact information:
   - **Callsign** - Station worked (auto-uppercase)
   - **Frequency** - Operating frequency in MHz
   - **Mode** - Select from dropdown (SSB, CW, Digital)
   - **RST Sent/Received** - Signal reports
   - **Exchange** - WFD exchange (format: `[Number][Class] Section`)
3. Click **Log Contact** to save

### Exchange Format
Winter Field Day exchanges follow the format: `[Number][Class] [Section]`

**Examples:**
- `2M EPA` - 2 transmitters, Mobile, EPA section
- `1H GA` - 1 transmitter, Home, Georgia section
- `3O WTX` - 3 transmitters, Outdoor, West Texas section

**Valid Classes:**
- **H** - Home station
- **I** - Indoor station  
- **O** - Outdoor station
- **M** - Mobile station

### Viewing Statistics
- **All Contacts** - View and manage all logged contacts
- **Statistics** - Band activity charts and contest analytics
- **Objectives** - Track WFD bonus objectives progress

### Exporting Logs
1. Go to **All Contacts** page
2. Click the **Export Log** dropdown
3. Choose format:
   - **Cabrillo (.log)** - For contest submission
   - **ADIF (.adif)** - For general logging software

## 🛠️ Configuration

### Station Setup
Configure your station information in the **Station Setup** page:
- Station callsign
- Contest class (H/I/O/M)
- ARRL section
- Timezone (auto-detected from ARRL section or manual override)
- Number of transmitters
- Operator callsigns

### Real-Time Clock
- Displays GMT and local time in the navigation bar
- Local time automatically determined from station's ARRL section
- Supports all US/Canadian timezones including Alaska, Hawaii, and Atlantic zones
- Updates every second for accurate timing during contest operations

### Comprehensive Theme System
- **26 Total Themes** - Extensive theme collection with light and dark variants
- **Basic Themes** - Light and Dark modes
- **School Colors** - Auburn, Alabama, Georgia, LSU, Florida, Tennessee, Texas A&M (light/dark variants)
- **Military Themes** - Army, Navy, Air Force, Marines (light/dark variants) 
- **Seasonal Themes** - Snow/Winter, USA Patriotic, Neon/Cyberpunk (light/dark variants)
- **Hybrid System** - Each themed option available in both light and dark modes
- **Persistent Preferences** - Theme selection automatically saved and restored
- **Accessible Design** - High contrast buttons and readable text across all themes

### Keyboard Shortcuts System
WFDpy includes a comprehensive keyboard shortcuts system designed for rapid contest logging and power user efficiency.

#### Navigation Shortcuts (Global)
- `Alt+H` - Go to Home page
- `Alt+L` - Go to Log Contact page  
- `Alt+C` - View All Contacts
- `Alt+S` - View Statistics
- `Alt+M` - View Contact Map
- `Alt+O` - View Objectives
- `Alt+T` - Station Setup

#### Form Field Shortcuts (Log Contact Page)
- `Alt+1` - Focus Callsign field
- `Alt+2` - Focus Frequency field
- `Alt+3` - Focus Mode field
- `Alt+4` - Focus RST Sent field
- `Alt+5` - Focus RST Received field
- `Alt+6` - Focus Exchange Received field
- `Alt+7` - Focus Notes field

#### Quick Value Shortcuts
- `Ctrl+5` - Set RST to 599
- `Ctrl+9` - Set RST to 59
- `Ctrl+P` - Set mode to SSB (Phone)
- `Ctrl+C` - Set mode to CW
- `Ctrl+D` - Set mode to Digital

#### Action Shortcuts
- `Ctrl+Enter` - Submit current form
- `Ctrl+R` - Clear/Reset form
- `Alt+N` - New contact (clear form)
- `Enter` - Move to next field (in forms)
- `Tab` - Next field
- `Shift+Tab` - Previous field
- `Escape` - Cancel/Clear or close modals

#### Utility Shortcuts
- `F1` - Show keyboard shortcuts help
- `Alt+?` - Show keyboard shortcuts help  
- `Ctrl+/` - Enable/disable shortcuts
- `Alt+D` - Toggle between light/dark theme variants
- `Ctrl+T` - Open theme selector

#### Rapid Contact Logging Example
Here's a typical rapid logging workflow using keyboard shortcuts:

1. `Alt+L` - Navigate to Log Contact page
2. `Alt+1` - Focus callsign field, type callsign
3. `Enter` - Move to frequency field, enter frequency
4. `Enter` - Move to mode field
5. `Ctrl+P` - Set mode to SSB
6. `Enter` - Move to RST sent field
7. `Ctrl+5` - Set RST to 599
8. `Enter` - Move to RST received field
9. `Ctrl+5` - Set RST to 599
10. `Enter` - Move to exchange received field
11. Type exchange information
12. `Ctrl+Enter` - Submit the contact

**Power User Tips:**
- Press `F1` on any page for complete shortcuts reference
- Use `Ctrl+/` to temporarily disable shortcuts if needed
- `Alt+D` provides quick theme switching during long contests
- `Escape` key quickly clears fields or closes dialog boxes
- Form labels show shortcut hints (e.g., `Alt+1` next to Callsign)

#### Keyboard Shortcuts Help
- Click the keyboard icon (🎹) in the navigation bar for interactive help
- All shortcuts are context-aware and work appropriately on different pages
- Shortcuts won't interfere with normal typing in input fields

## 📸 Screenshots

### Home Page - Light Mode
![Home Page Light Mode](screen%20caps/Screenshot%202025-09-04%20113542.png)
*Main dashboard showing real-time GMT/Central time clock, contest countdown, station information, and quick actions in light theme*

### Home Page - Dark Mode  
![Home Page Dark Mode](screen%20caps/Screenshot%202025-09-04%20113419.png)
*Same dashboard in dark mode, demonstrating the seamless theme integration with the real-time clock*

### Contact Logging - Real-time Clock Integration
![Contact Logging](screen%20caps/Screenshot%202025-09-04%20113439.png)
*Log contact form showing the navigation clock working during active contest operations*

### Station Setup - Timezone Configuration
![Station Setup](screen%20caps/Screenshot%202025-09-04%20113510.png)
*Station configuration page where timezone can be set automatically from ARRL section or manually overridden*

### Statistics Dashboard
![Statistics Page](screen%20caps/Screenshot%202025-09-04%20113451.png)
*Comprehensive statistics view with real-time clock for timing reference during contest analysis*

### Contest Map - ARRL Sections
![Contact Map](screen%20caps/Screenshot%202025-09-04%20113500.png)
*Interactive map showing worked ARRL sections with timezone-aware clock for coordination*

### WFD Objectives Tracking
![WFD Objectives](screen%20caps/Screenshot%202025-09-04%20113519.png)
*Bonus objective tracking with multiplier management and real-time timing*

### Official Rules Reference
![WFD Rules](screen%20caps/Screenshot%202025-09-04%20113528.png)
*Built-in rules reference with contest timing information and real-time clock for quick reference*

## 📊 Contest Features

### Winter Field Day Scoring
- **Contact Points**: Varies by band and mode
- **Multipliers**: ARRL sections worked
- **Bonus Points**: Special WFD objectives
- **Real-time Calculation**: Updates as contacts are logged

### Objectives Tracking
Monitor progress on WFD bonus objectives:
- Work all contest bands
- Work multiple modes
- Complete digital contacts
- Educational activities
- And more...

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run focused tests
python test_focused.py

# Run all tests
python -m pytest
```

The application includes extensive testing covering:
- Web routes and functionality
- Database operations
- Band/frequency conversions
- Form validation
- Export functionality

## 📁 Project Structure

```
WFDpy/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── .gitignore           # Git ignore rules
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── log.html         # Contact logging
│   ├── contacts.html    # Contact management
│   ├── stats.html       # Statistics
│   └── ...
├── static/              # Static assets
│   └── css/
│       └── dark-mode.css # Dark theme styles
└── tests/              # Test files
    ├── test_focused.py
    └── ...
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`python test_focused.py`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/WFDpy.git
cd WFDpy

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_focused.py
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Winter Field Day Association** - For organizing Winter Field Day
- **Amateur Radio Community** - For inspiration and feedback
- **Flask Team** - For the excellent web framework
- **Bootstrap** - For the responsive UI components
- **Chart.js** - For beautiful data visualizations

## 📞 Support

If you encounter issues or have questions:

1. Check the [Issues](https://github.com/shadowhegemon/WFDpy/issues) page
2. Create a new issue with detailed information
3. Include error messages and steps to reproduce

## 🔄 Version History

- **v1.0.0** - Initial release with full WFD logging functionality
  - Complete contest logging system
  - Real-time scoring and statistics
  - Dark mode support
  - Export capabilities
  - Comprehensive test coverage

## 🎯 Future Enhancements

- Contest announcement and bulletin display
- Backup and restore functionality
- Enhanced mobile interface
- Real-time propagation data
- Network logging support
- Additional export formats

---

**73! Happy contesting!** 📻

*WFDpy - Making Winter Field Day logging simple and efficient.*