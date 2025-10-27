# Network-based OSINT Investigation Tool

An open-source intelligence (OSINT) investigation tool built with Python and Flask. This application consolidates multiple data sources to investigate IP addresses and domains, retrieving WHOIS data, geolocation information, and port scanning results through a web-based interface.

## Features

**Information Gathering**
- IP address and domain name resolution using DNS queries
- WHOIS and RDAP data retrieval for network registration information
- Geolocation lookup with precise latitude and longitude coordinates
- Open port detection and service identification via Shodan API integration

**Data Presentation**
- Web-based interface with organized card layout displaying results
- Interactive maps showing geographic location of investigated IP addresses
- Structured JSON export of investigation results
- Responsive design supporting various screen sizes

**Integration**
- Official Shodan API integration for port and service scanning
- ipinfo.io geolocation API for coordinate and location data
- OpenStreetMap tile provider for geographic visualization

## Libraries Used

### Python Standard Library

**socket**
- Purpose: Performs DNS resolution to convert domain names into IP addresses
- Implementation: Used in the `resolve_domain()` function to query system DNS resolvers
- Benefit: Built-in module, no external dependencies required
- Functionality: Enables automatic IP lookup when users provide domain names

### External Python Packages

**ipwhois**
- Purpose: Retrieves WHOIS and RDAP (Registration Data Access Protocol) information for IP addresses
- Implementation: Queries WHOIS/RDAP databases to extract autonomous system numbers (ASN), organization names, and network descriptions
- Key Data Retrieved: ASN, organization name, network range, country code
- Benefit: Simplifies complex WHOIS parsing; handles both legacy WHOIS and modern RDAP protocols

**requests**
- Purpose: Handles HTTP requests to external APIs for data retrieval
- Implementation: Makes GET requests to ipinfo.io geolocation API
- Functionality: Retrieves geographic coordinates, city, country, and organization information
- Error Handling: Manages connection timeouts and HTTP errors gracefully

**shodan**
- Purpose: Official Shodan Python library for port scanning and service discovery
- Implementation: Queries Shodan's search engine API to identify open ports and running services on target IP addresses
- Key Data Retrieved: Port numbers, protocols, software versions, service banners
- API Integration: Requires optional API key for full functionality; tool operates with limited features when key is unavailable
- Benefit: Eliminates manual HTTP error handling; provides structured data responses

**flask**
- Purpose: Lightweight web framework for building the HTTP server and user interface
- Implementation: Handles routing (GET requests to home page, POST requests for investigation), template rendering, and response serving
- Components: Routes incoming requests, serves static files, renders Jinja2 templates
- Benefit: Simplifies web application development; minimal overhead for this use case

**json**
- Purpose: Serializes and deserializes investigation results for storage and transmission
- Implementation: Converts Python dictionaries to JSON format for HTML report generation and data export
- Functionality: Enables structured data storage and API response handling
- Standard Library: No external dependencies required

### Frontend Libraries

**Leaflet.js**
- Purpose: Interactive mapping library for displaying geolocation data on web pages
- Implementation: Renders OpenStreetMap tiles and adds location markers with information popups
- Features: Zoom controls, pan functionality, marker clustering, popup information displays
- Integration: Embedded directly in HTML template; communicates with JavaScript to place markers at retrieved coordinates
- Benefit: Lightweight alternative to heavier mapping solutions; no API key required for OpenStreetMap tiles

## Installation

### Requirements
- Python 3.8 or higher
- pip package manager

### Setup Instructions

1. Navigate to project directory:
   ```bash
   cd OSint_P1
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Configure Shodan API access:
   - Visit https://account.shodan.io/ and create an account
   - Retrieve your API key from the account dashboard
   - Edit osint_tool.py and update the SHODAN_API_KEY variable:
     ```python
     SHODAN_API_KEY = 'your_api_key_here'
     ```
   - Note: The tool functions without this key, but port scanning capabilities are disabled

## Usage

### Web Application

Start the Flask application:
```bash
python osint_tool.py
```

Access the web interface at http://127.0.0.1:5000

Enter an IP address (e.g., 8.8.8.8) or domain name (e.g., google.com) and click the Investigate button. Results are displayed in organized sections:

- Target Information: Shows input and resolved IP address
- Port and Service Scanning: Lists open ports and services (if Shodan API key is configured)
- WHOIS Information: Displays ASN, organization name, and network details
- Geolocation: Presents location coordinates and displays marker on interactive map

## Example Investigation

Query: 1.1.1.1

Expected output:
```
Target Information:
  IP Address: 1.1.1.1
  Domain: one.one.one.one

Port and Service Scanning:
  Open Ports: 53, 80, 443
  Services: DNS, HTTP, HTTPS

WHOIS Information:
  ASN: 13335
  Organization: Cloudflare Inc
  Network Range: 1.1.1.0/24
  Country: AU

Geolocation:
  City: Brisbane
  Country: Australia
  Coordinates: -27.4816, 153.0175
  Map: Interactive visualization
```

## Project Structure

```
OSint_P1/
├── osint_tool.py              # Main Flask application and investigation functions
├── templates/
│   └── index.html             # Web interface template
├── requirements.txt           # Python package dependencies
└── README.md                  # Documentation
```

## Architecture

The application follows a three-tier architecture:

**Backend (osint_tool.py)**
- Flask web server handling HTTP requests
- Investigation functions: resolve_domain(), get_whois(), get_geo(), get_shodan()
- Error handling and data aggregation
- JSON response formatting

**Frontend (templates/index.html)**
- Form input for IP addresses and domain names
- Results display in card layout
- Leaflet.js map integration for geolocation visualization
- CSS styling for responsive design

**External Data Sources**
- DNS (system resolver)
- WHOIS/RDAP databases (via ipwhois)
- ipinfo.io API for geolocation
- Shodan search engine API (optional)

## Data Flow

1. User submits IP address or domain name through web interface
2. osint_tool.py receives POST request with target input
3. Application processes investigation in parallel:
   - DNS resolution of domain name (if applicable)
   - WHOIS/RDAP lookup for network registration data
   - Geolocation API query for coordinates and location
   - Shodan API query for port and service information (if key available)
4. Results aggregated into JSON response
5. Frontend renders results in organized cards
6. Map displays geolocation marker at retrieved coordinates

## Data Sources

**DNS Resolution**
- Source: System DNS resolver via socket library
- Data: IP addresses corresponding to domain names

**WHOIS Information**
- Source: WHOIS/RDAP registries via ipwhois library
- Data: Autonomous system numbers, organization names, network ranges

**Geolocation**
- Source: ipinfo.io API
- Data: Geographic coordinates, city, country, organization

**Port Scanning**
- Source: Shodan search engine API
- Data: Open ports, running services, service banners
- Availability: Requires Shodan API key

## Technical Considerations

### Error Handling
The application implements error handling for common failure scenarios:
- Invalid IP addresses or unreachable domains
- Timeout responses from external APIs
- Missing or rate-limited Shodan API keys
- Network connectivity issues

### Performance
- Average investigation completion time: 2-5 seconds
- Response time dependent on external API availability
- Geolocation map loads asynchronously after initial results display

### Limitations
- Requires internet connectivity to access external APIs
- Shodan port scanning requires API key and paid subscription for comprehensive data
- Geographic accuracy dependent on ipinfo.io database
- DNS resolution limited to forward lookups only

## Disclaimer

This tool is intended for educational and authorized security research purposes. Users are responsible for obtaining proper authorization before investigating any IP addresses or domains. Unauthorized network investigation may violate applicable laws and regulations.
