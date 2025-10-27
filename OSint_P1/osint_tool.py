import socket
import json
from ipwhois import IPWhois
import requests
from flask import Flask, render_template, request
import shodan

app = Flask(__name__)

# Replace with your actual Shodan API key
SHODAN_API_KEY = 'FidfPxQqito0VScDhgI3UXGJBGD9cRGk'

@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        target = request.form['target'].strip()
        results = investigate(target)
    return render_template('index.html', results=results)

def investigate(target):
    """
    Main investigation function.
    """
    # Strip protocol if present (e.g., https://domain.com -> domain.com)
    if '://' in target:
        target = target.split('://')[1].split('/')[0]
    
    # Determine if target is IP or domain
    if '.' in target and not target.replace('.', '').replace('/', '').isdigit():
        print(f"Resolving domain: {target}")
        ip = resolve_domain(target)
        if not ip:
            return {'error': 'Failed to resolve domain'}
    else:
        ip = target

    print(f"Investigating IP: {ip}")

    # Gather data
    whois_data = get_whois(ip)
    geo_data = get_geo(ip)
    shodan_data = get_shodan(ip)

    # Compile results
    results = {
        'target': target,
        'ip': ip,
        'whois': whois_data,
        'geolocation': geo_data,
        'shodan': shodan_data
    }

    return results

def resolve_domain(domain):
    """
    Resolves a domain name to an IP address.
    """
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror as e:
        print(f"Error resolving domain: {e}")
        return None

def get_whois(ip):
    """
    Retrieves WHOIS information for the IP, including ASN and organization.
    """
    try:
        obj = IPWhois(ip)
        results = obj.lookup_rdap()
        return {
            'asn': results.get('asn'),
            'asn_description': results.get('asn_description'),
            'network_name': results.get('network', {}).get('name'),
            'organization': results.get('network', {}).get('name')  # Approximate organization
        }
    except Exception as e:
        return {'error': f'WHOIS lookup failed: {str(e)}'}

def get_geo(ip):
    """
    Retrieves geolocation information for the IP using ipinfo.io.
    """
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json', timeout=10)
        response.raise_for_status()
        data = response.json()
        loc = data.get('loc', '')
        if loc:
            lat, lon = loc.split(',')
            lat = float(lat)
            lon = float(lon)
        else:
            lat = lon = None
        return {
            'country': data.get('country'),
            'city': data.get('city'),
            'latitude': lat,
            'longitude': lon,
            'organization': data.get('org')
        }
    except requests.RequestException as e:
        return {'error': f'Geolocation lookup failed: {str(e)}'}
    except ValueError:
        return {'error': 'Invalid location data'}

def get_shodan(ip):
    """
    Retrieves open port and service data from Shodan API using the official library.
    """
    if SHODAN_API_KEY == 'your_shodan_api_key_here':
        return {'error': 'Shodan API key not configured. Get a free API key from https://account.shodan.io/'}

    try:
        # Initialize the Shodan API client
        api = shodan.Shodan(SHODAN_API_KEY)

        # Get host information
        host = api.host(ip)

        ports = host.get('ports', [])
        services = []

        # Extract services from host data
        for service_data in host.get('data', []):
            if service_data.get('product'):
                services.append(service_data['product'])

        return {
            'ports': ports,
            'services': list(set(services))  # Remove duplicates
        }

    except shodan.APIError as e:
        error_msg = str(e)
        if 'Invalid API key' in error_msg or 'access denied' in error_msg.lower():
            return {'error': 'Shodan API key is invalid or expired. Get a new free API key from https://account.shodan.io/'}
        elif 'No information available' in error_msg or 'not found' in error_msg.lower():
            return {'error': 'No Shodan data available for this IP address'}
        else:
            return {'error': f'Shodan API Error: {error_msg}'}
    except Exception as e:
        return {'error': f'Shodan lookup failed: {str(e)}'}

if __name__ == '__main__':
    app.run(debug=True)