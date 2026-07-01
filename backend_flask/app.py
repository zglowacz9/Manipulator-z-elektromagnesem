from flask import Flask, redirect, render_template, request, jsonify, session, url_for, render_template_string
from datetime import datetime

app = Flask(__name__)
# Klucz do szyfrowania sesji logowania
app.secret_key = 'super-tajny-klucz-bez-bazy-danych'

# --- AKUTALNY STAN ROBOTA (Zamiast bazy danych, trzymamy w pamięci RAM) ---
stan_robota = {
    27: {"value": 90.0, "quantity": "angle", "unit": "deg"},
    26: {"value": 90.0, "quantity": "speed", "unit": "raw"},
    25: {"value": 90.0, "quantity": "speed", "unit": "raw"},
    99: {"value": 0.0, "quantity": "state", "unit": "bin"}
}

UZYTKOWNICY = {
    "admin": "admin",
    "Orthoget": "alamakota"
}

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        input_username = request.form["username"]
        input_password = request.form["password"]
        
        # Weryfikacja "na sztywno" na podstawie naszego słownika
        if input_username in UZYTKOWNICY and UZYTKOWNICY[input_username] == input_password:
            session["zalogowany"] = True
            session["username"] = input_username
            return redirect(url_for("panel_sterowania"))
        else:
            error = "Niepoprawny login lub hasło! Spróbuj ponownie."

    html_login = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logowanie - Robot IoT</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e24; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .login-box { background: #2a2a35; padding: 40px; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); width: 320px; text-align: center; }
            h2 { color: #00adb5; margin-bottom: 25px; }
            input[type="text"], input[type="password"] { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #222; color: #fff; box-sizing: border-box; }
            .btn-login { width: 100%; padding: 12px; background: #00adb5; border: none; color: white; font-weight: bold; border-radius: 8px; cursor: pointer; font-size: 16px; margin-top: 15px; transition: 0.2s; }
            .btn-login:hover { background: #008c95; }
            .error-msg { color: #d9534f; margin-bottom: 15px; font-size: 14px; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Autoryzacja</h2>
            {% if error %}
                <div class="error-msg">{{ error }}</div>
            {% endif %}
            <form method="post">
                <input type="text" name="username" placeholder="Nazwa użytkownika (Login)" required autofocus>
                <input type="password" name="password" placeholder="Hasło" required>
                <button type="submit" class="btn-login">Zaloguj się</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_login, error=error)


@app.route("/logout")
def logout():
    session.pop("zalogowany", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
def panel_sterowania():
    if not session.get("zalogowany"):
        return redirect(url_for("login"))

    html_panel = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel Sterowania Robotem IPZ</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #1e1e24; color: #fff; text-align: center; padding: 20px; }
            .container { max-width: 600px; margin: 0 auto; background: #2a2a35; padding: 30px; border-radius: 15px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }
            .header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px solid #333; padding-bottom: 15px; }
            h1 { color: #00adb5; margin: 0; font-size: 24px; }
            .logout-link { color: #d9534f; text-decoration: none; font-weight: bold; border: 1px solid #d9534f; padding: 5px 12px; border-radius: 5px; transition: 0.2s; }
            .logout-link:hover { background: #d9534f; color: white; }
            .control-card { background: #333344; padding: 20px; margin-bottom: 20px; border-radius: 10px; text-align: left; }
            .control-card label { font-size: 18px; font-weight: bold; display: block; margin-bottom: 10px; }
            .slider-container { display: flex; align-items: center; gap: 15px; }
            input[type=range] { flex-grow: 1; height: 8px; border-radius: 5px; accent-color: #00adb5; cursor: pointer; }
            .val-display { font-size: 20px; font-weight: bold; min-width: 50px; text-align: right; color: #00adb5; }
            .btn { display: block; width: 100%; padding: 15px; font-size: 20px; font-weight: bold; color: white; border: none; border-radius: 8px; cursor: pointer; transition: 0.2s; }
            .btn-on { background: #393e46; border: 2px solid #00adb5; color: #00adb5; }
            .btn-on:hover { background: #00adb5; color: white; }
            .btn-danger { background: #d9534f; }
            .btn-danger:hover { background: #c9302c; }
            .user-info { font-size: 14px; color: #888; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-flex">
                <div>
                    <h1> Panel Sterowania Robotem </h1>
                    <span class="user-info">Zalogowany jako: <b>{{ session['username'] }}</b></span>
                </div>
                <a href="/logout" class="logout-link">Wyloguj</a>
            </div>
            
            <div class="control-card">
                <label> Serwo A (Podstawa - Pin 27)</label>
                <div class="slider-container">
                    <input type="range" min="0" max="180" value="90" id="servoA" onchange="wyslijRozkaz(27, this.value, 'angle', 'deg')">
                    <span class="val-display" id="valA">90°</span>
                </div>
            </div>

            <div class="control-card">
                <label> Serwo B (Ramie - Pin 26)</label>
                <div class="slider-container">
                    <input type="range" min="0" max="180" value="90" id="servoB" onchange="wyslijRozkaz(26, this.value, 'speed', 'raw')">
                    <span class="val-display" id="valB">90</span>
                </div>
            </div>

            <div class="control-card">
                <label> Serwo C (Efektor - Pin 25)</label>
                <div class="slider-container">
                    <input type="range" min="0" max="180" value="90" id="servoC" onchange="wyslijRozkaz(25, this.value, 'speed', 'raw')">
                    <span class="val-display" id="valC">90</span>
                </div>
            </div>

            <div class="control-card" style="text-align:center;">
                <label style="text-align:left;"> Elektromagnes (Pin 32)</label>
                <div style="display:flex; gap:10px; margin-top:10px;">
                    <button class="btn btn-on" onclick="wyslijRozkaz(99, 1.0, 'state', 'bin')">ZŁAP (WŁ)</button>
                    <button class="btn btn-danger" onclick="wyslijRozkaz(99, 0.0, 'state', 'bin')">PUŚĆ (WYŁ)</button>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('servoA').oninput = function() { document.getElementById('valA').innerText = this.value + '°'; }
            document.getElementById('servoB').oninput = function() { document.getElementById('valB').innerText = this.value; }
            document.getElementById('servoC').oninput = function() { document.getElementById('valC').innerText = this.value; }

            function wyslijRozkaz(pinIndex, wartosc, cecha, jednostka) {
                fetch('/zapisz_rozkaz_panelu', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        pin: pinIndex,
                        value: parseFloat(wartosc),
                        quantity: cecha,
                        unit: jednostka
                    })
                })
                .then(res => res.json())
                .then(data => console.log("Zapisano w RAM:", data))
                .catch(err => console.error("Błąd zapisu:", err));
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html_panel)


@app.route("/zapisz_rozkaz_panelu", methods=["POST"])
def zapisz_rozkaz_panelu():
    if not session.get("zalogowany"):
        return jsonify({"status": "error", "message": "Brak autoryzacji"}), 401

    pin = int(request.json['pin'])
    value = request.json['value']
    quantity = request.json['quantity']
    unit = request.json['unit']
    
    # Aktualizujemy globalny słownik w pamięci serwera
    stan_robota[pin] = {
        "value": value,
        "quantity": quantity,
        "unit": unit
    }
    
    return jsonify({"status": "success", "saved_value": value, "pin": pin})


# ==========================================
# 2. ENDPOINT DLA ROBOTA ESP32 (Bez logowania)
# ==========================================

@app.route("/device/<int:device_id>/joint/<int:joint_index>/latest", methods=["GET"])
def get_latest_joint_command(device_id, joint_index):
    # Zwracamy dane prosto z naszego słownika w RAM
    if joint_index in stan_robota:
        return jsonify(stan_robota[joint_index]), 200
    else:
        # Awaryjna domyślna wartość, jeśli ESP32 zapyta o dziwny pin
        return jsonify({"value": 90.0 if joint_index != 99 else 0.0}), 200
