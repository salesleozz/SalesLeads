from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from scraper.instagram import run_instaleads
from scraper.scraper import run_scraper
from scraper.marketplace import run_produtos
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'nb+)#frdr_u1f8pt9)j3etf6ag1b%ws^wc-xi4-&@89lswh(p$'

db_maps = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'google_maps',
}

db_insta = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'insta_leads',
}

db_market = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'marketplaces',
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scraper', methods=['GET', 'POST'])
def scraper():
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        try:
            run_scraper(pesquisa, db_maps)
            flash(f'A raspagem de "{pesquisa}" foi concluída!', 'success')
        except Exception as e:
            flash(f'Houve um erro durante a raspagem: {str(e)}', 'danger')
        return redirect(url_for('scraper'))
    return render_template('scraper.html')

@app.route('/instagram', methods=['GET', 'POST'])
def instagram():
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        try:
            run_instaleads(pesquisa, db_insta)
            flash(f'A raspagem de "{pesquisa}" foi concluída!', 'success')
        except Exception as e:
            flash(f'Houve um erro durante a raspagem: {str(e)}', 'danger')
        return redirect(url_for('instagram'))
    return render_template('insta.html')

@app.route('/marketplace', methods=['GET', 'POST'])
def marketplace():
    if request.method == 'POST':
        pesquisa = request.form['pesquisa']
        place = request.form['place']
        try:
            run_produtos(pesquisa, place, db_market)
            flash(f'A raspagem de "{pesquisa}" foi concluída!', 'success')
        except Exception as e:
            flash(f'Houve um erro durante a raspagem: {str(e)}', 'danger')
        return redirect(url_for('marketplace'))
    return render_template('marketplace.html')


if __name__ == '__main__':
    app.run(debug=True)
