from flask import Flask, request, render_template, redirect, url_for, session, flash
from supabase import create_client, Client
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Supabase настройки
url = "https://jnppdplocmgtckjnugza.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImpucHBkcGxvY21ndGNram51Z3phIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU5MjI0NTMsImV4cCI6MjA2MTQ5ODQ1M30.6xwBizgEmxCsMRv72OZHWBVVqzjrTTLXiR68TitENHI"
supabase: Client = create_client(url, key)


# Функция за регистрация на потребител
def register_user(email, password, nickname):
    # Проверка дали email вече съществува
    existing_user = supabase.auth.api.get_user_by_email(email)
    if existing_user:
        return {"status_code": 400, "message": "Email already in use."}

    response = supabase.auth.sign_up(email=email, password=password)
    if response.status_code == 200:
        user_id = response.data['user']['id']
        supabase.table("users").upsert({"user_id": user_id, "nickname": nickname}).execute()
        return response
    else:
        return {"status_code": response.status_code, "message": "Registration failed. Please try again."}


# Функция за вход на потребител
def login_user(email, password):
    try:
        # Използвай правилния метод за влизане
        response = supabase.auth.sign_in({
            'email': email,
            'password': password
        })

        # Проверка за грешки
        if response.get("error"):
            return {"status_code": 400, "message": "Invalid credentials. Please try again."}

        return response
    except Exception as e:
        return {"status_code": 500, "message": str(e)}


# Функция за добавяне на тренировка
def add_training(user_id, date, status):
    data = {
        "user_id": user_id,
        "date": date,
        "status": status
    }
    response = supabase.table("trainings").insert(data).execute()
    return response


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    today = datetime.now().strftime('%Y-%m-%d')

    if request.method == 'POST':
        date = request.form['date']
        answer = request.form['answer']
        user_id = session['user_id']
        add_training(user_id, date, answer)
        return redirect(url_for('success'))

    return render_template('index.html', today=today)


@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/history', methods=['GET', 'POST'])
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    selected_month = request.form.get('month') if request.method == 'POST' else None

    if selected_month:
        result = supabase.table("trainings").select("*").eq("user_id", user_id).like("date",
                                                                                     f"{selected_month}%").execute()
    else:
        result = supabase.table("trainings").select("*").eq("user_id", user_id).execute()

    values = result.data
    return render_template('history.html', values=values, month=selected_month)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        nickname = request.form['nickname']
        response = register_user(email, password, nickname)

        if response["status_code"] == 200:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash(response["message"], 'danger')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response = login_user(email, password)

        if response["status_code"] == 200:
            session['user_id'] = response['data']['user']['id']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash(response["message"], 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
