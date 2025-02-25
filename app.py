from flask import Flask, request, jsonify
import psycopg2
from geopy.distance import geodesic

app = Flask(__name__)

# Database Connection (Supabase/PostgreSQL)
DB_PARAMS = {
    'dbname': 'your_database',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_host',
    'port': 'your_port'
}


def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

# Register User API
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = data['user_id']
    role = data['role']  # "seeker" or "provider"
    lat = data['latitude']
    lon = data['longitude']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, role, latitude, longitude, paid) VALUES (%s, %s, %s, %s, %s)", 
                (user_id, role, lat, lon, False))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "User registered successfully!"})

# Payment Confirmation API
@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    user_id = data['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET paid = %s WHERE user_id = %s", (True, user_id))
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"message": "Payment confirmed!"})

# Match Seekers to Providers API
@app.route('/match', methods=['POST'])
def match():
    data = request.json
    user_id = data['user_id']
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the seeker’s location
    cur.execute("SELECT latitude, longitude FROM users WHERE user_id = %s AND role = 'seeker'", (user_id,))
    seeker = cur.fetchone()
    if not seeker:
        return jsonify({"error": "Seeker not found!"})
    seeker_location = (seeker[0], seeker[1])
    
    # Get providers within 10 km
    cur.execute("SELECT user_id, latitude, longitude FROM users WHERE role = 'provider'")
    providers = cur.fetchall()
    
    nearby_providers = []
    for provider in providers:
        provider_location = (provider[1], provider[2])
        distance = geodesic(seeker_location, provider_location).km
        if distance <= 10:
            nearby_providers.append({"provider_id": provider[0], "distance_km": distance})
    
    cur.close()
    conn.close()
    
    return jsonify({"providers": nearby_providers})

if __name__ == '__main__':
    app.run(debug=True)
