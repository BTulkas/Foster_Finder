from werkzeug.utils import redirect

from main import app
from flask import render_template, flash, url_for

from main.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    test_user = {'username': 'Test1'}
    return render_template('index.html', title="Made It", user=test_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_to_render = LoginForm()
    if form_to_render.validate_on_submit()():
        flash('Login requested for user {}, remember_me={}'.format(
            form_to_render.email.data, form_to_render.remember_me.data
        ))
        return redirect(url_for('/index'))
    return render_template('login.html', title='Sign In', form=form_to_render)
