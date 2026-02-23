from flask import Flask, render_template, jsonify, request
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# The local APIs we need to proxy
APIS = {
    'ux': 'http://localhost:9000/ux-agent-latest',
    'delivery': 'http://localhost:9578',
    'churn': 'http://localhost:4996/api/churn/latest', # Updated endpoint
    'food': 'http://localhost:4782/api/dashboard'
}

def fetch_api(name, url):
    """Helper function to fetch data from a single API."""
    try:
        # 2-second timeout so a dead API doesn't hang the whole dashboard
        response = requests.get(url, timeout=2) 
        response.raise_for_status()
        return name, response.json(), None
    except Exception as e:
        return name, None, str(e)

@app.route('/')
def index():
    """Serves the main HTML dashboard."""
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Fetches data from all agent APIs concurrently and returns a single JSON object."""
    results = {}
    
    # Use ThreadPoolExecutor to fetch all 4 APIs at the same time (faster than sequential)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_api, name, url) for name, url in APIS.items()]
        
        for future in futures:
            name, data, error = future.result()
            results[name] = {
                'status': 'success' if data else 'error',
                'data': data,
                'error': error
            }
            
    return jsonify(results)

@app.route('/api/send-sms', methods=['POST'])
def send_sms():
    """Securely handles calling the Twilio API from the server."""
    data = request.json
    holistic_index = data.get('index', '0.00')
    status_text = data.get('status', 'Unknown')

    # Your Twilio Credentials
    account_sid = 'AC86e3df611e88e20034b88b6c60a99036'
    auth_token = 'c890806589549c5fd84bd3bff3be6c6d'
    from_number = '+16578375821'
    to_number = '+919819343304'

    message_body = f"Agentic AI For Food Delivery Update:\nHolistic Index: {holistic_index}\nStatus: {status_text}"
    twilio_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"

    try:
        # Make the request from the backend
        response = requests.post(
            twilio_url,
            auth=(account_sid, auth_token),
            data={
                'To': to_number,
                'From': from_number,
                'Body': message_body
            }
        )
        
        if response.status_code in [200, 201]:
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": response.text}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Running on port 6901 by default
    app.run(host='0.0.0.0', port=6901, debug=True)