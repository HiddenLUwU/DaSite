import os
import sqlite3
from flask import Flask, render_template, redirect, request
from data import db_session, plants_api
from data.users import User
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import DataRequired
from requests import post
from W.forms.sending_form import SendingForm


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("W/db/garden_site.db")
    app.register_blueprint(plants_api.blueprint)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    user = User()
    user.name = "Пользователь 1"
    user.about = "биография пользователя 1"
    user.email = "email@email.ru"
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()


# h1 - Заголовки
# h2 - текст в хедере
# h3 - основной текст
# h4 - это h3 но без отступа
# h5
# h6
@app.route("/main")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        sussy = 'Вы вошли в аккаунт'
    else:
        sussy = 'Вы не вошли в аккаунт'
    return render_template("main.html", acc=sussy)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.nickname.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/main")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/plants/<plant>', methods=['GET', 'POST'])
def planttt(plant):
    form = SendingForm()
    connect = sqlite3.connect('W/db/garden_site.db')
    cur = connect.cursor()
    res1 = cur.execute(f"SELECT pictures FROM Plant WHERE name = '{plant}'").fetchall()
    res2 = cur.execute(f"SELECT info FROM Plant WHERE name = '{plant}'").fetchall()
    if '_' in plant:
        pl_name = plant.split('_')[0]
    else:
        pl_name = plant
    res3 = cur.execute(f"SELECT message, image, sender, "
                       f"created_date FROM chats WHERE plant = '{pl_name}'").fetchall()
    connect.close()
    information = res2[0][0].split('%')
    pictures = res1[0][0].split('%')
    growing = information[9].split('$')
    facts = information[11].split('$')
    messages = []
    for el in res3:
        messages.append((f'{el[0]}', f'/static/img/chats_pics/{el[1]}', el[2], el[3]))
    if request.method == 'GET':
        return render_template('plants.html', plant=plant, pics=pictures, info=information, grow=growing,
                               facts=facts, a=len(messages), messages=messages, form=form)
    elif request.method == 'POST':
        connect = sqlite3.connect('W/db/garden_site.db')
        cur = connect.cursor()
        res1 = cur.execute(f'SELECT id FROM chats').fetchall()
        a = len(res1) + 1
        f = form.image.data
        data = f.read()
        if form.validate_on_submit():
            with open(f'W/static/img/chats_pics/{plant}_{a}.png', mode="wb") as picture:
                picture.write(data)
                print(picture)
            b = current_user.nickname
            c = f'{plant}_{a}.png'
            d = form.message.data
            print(
                post(f'http://localhost:5000/api/plants',
                     json={'plant': f'{pl_name}', 'message': f'{d}',
                           'image': f'{c}', 'sender': f'{b}'}).content)
            # res2 = cur.execute(f"INSERT INTO {pl_name}_chat VALUES({a},'{plant}_{a}.png','{current_user.nickname}')")
        connect.commit()
        connect.close()
        return redirect(f'/plants/{plant}')


@app.route('/plants_carrot')
def carrot():
    return render_template('plants_carrot.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/main")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


if __name__ == '__main__':
    main()
