'''
Simple flask api to test the Banhammer implementation
'''

from flask import Flask, request, jsonify
import events

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    # get the value from the request
    value = request.json.get('value')
    # get the ip address from the request
    ip_address = request.remote_addr
    if value == '1234':
        events.after_login_successful(ip_address)
        return jsonify({'success': True})
    else:
        events.after_login_failed
        return jsonify({'success': False})
    
@app.route('/status', methods=['GET'])
def status():
    ip = request.args.get('ip')
    return jsonify(events.report_login_successful(ip))

if __name__ == '__main__':
    app.run(debug=True)
    
'''
Sample output:
{
    "action": [
        "block_local"
    ],
    "action_duration": 3600,
    "count": 11,
    "limit": 10,
    "rate": 0.0030555555555555556,
    "window": 3600
}
'''