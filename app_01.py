import httpx
from datetime import datetime
from flask import Flask, render_template, request, abort, flash, url_for, redirect
from models_01 import UserIn

app = Flask(__name__)
app.secret_key = b'df40bb13e3125376d80767950a4499e165f2be7c35728768f2b9e4a8a8d39675'
"""
Генерация недёжного секретного ключа
>>> import secrets
>>> secrets.token_hex()
"""
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
# db.init_app(app)


@app.route('/')
def html_index():
    return render_template('index.html')


@app.route('/index/')
def index():
    context = {
        'title': 'Интернет магазин',
        'name': 'Харитон', }
    return render_template('index.html', **context)


# @app.errorhandler(404)
# def page_not_found(e):
#     app.logger.warning(e)
#     context = {
#         'title': 'Страница не найдена',
#         'url': request.base_url,
#     }
#     return render_template('404.html', **context), 404


@app.errorhandler(500)
def page_not_found(e):
    app.logger.error(e)
    context = {
        'title': 'Ошибка сервера',
        'url': request.base_url,
    }
    return render_template('500.html', **context), 500


@app.route('/form/', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Extract all form data
        name = request.form.get('input-name')
        email = request.form.get('input-email')
        password = request.form.get('input-password')
        age = request.form.get('input-age')
        birthdate_str = request.form.get('input-birthdate')
        phone = request.form.get('input-phone')
        checkbox = request.form.get('input-checkbox')  # Will return 'on' if checked

        # Simple validation for name, feel free to extend validation to other fields
        if not name:
            flash('Введите имя!', 'danger')
            return redirect(url_for('form'))

        try:
            # Parse the birthdate from string to a date object
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()

            user_in = UserIn(
                name=name,
                email=email,
                password=password,
                age=int(age),
                birthdate=birthdate,
                phone=phone,
                agreement=True if checkbox == 'on' else False
            )

            print(user_in)

            # Convert the date to string in YYYY-MM-DD format
            user_data = user_in.dict()
            user_data['birthdate'] = user_data['birthdate'].isoformat()  # Convert date to string

            # Send data to FastAPI
            response = httpx.post("http://127.0.0.1:8000/users/", json=user_data)
            response.raise_for_status()  # Raise an error for bad responses

            flash('Форма успешно отправлена!', 'success')
        except ValueError as e:
            # Handle errors such as incorrect age, birthdate, or missing data
            flash(f'Ошибка валидации данных: {str(e)}', 'danger')
            return redirect(url_for('form'))
        except httpx.HTTPStatusError as e:
            flash(f'Ошибка при отправке данных на сервер: {str(e)}', 'danger')
            return redirect(url_for('form'))

        # After form submission, redirect back to form
        return redirect(url_for('form'))
    return render_template('input_form.html')


if __name__ == '__main__':
    app.run(debug=True)