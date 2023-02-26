import sqlite3
from pathlib import Path
import cloudscraper
from re import findall as re_findall
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testsecretkeyforflask'

this_folder = Path(__file__).parent.resolve()


def get_db_connection():
    database_file = this_folder/'database.db'
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    return conn

def get_post(url_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM urls WHERE id = ?',
                        (url_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

def write_file(name, url):
    m3u_file = this_folder/'static/vod.m3u'
    with open(m3u_file,'a+') as f:
        f.write('\n#EXTINF:-1, tvg-logo="",{}\n'.format(name))
        f.write(url)
        f.write('\n')


def get_video_url_from_mdisk(url):
    check = re_findall(r"\bhttps?://.*mdisk\S+", url)
    if not check:
        textx = "**Invalid link**"
        print(textx)
    else:
        try:
            fxl = url.split("/")
            urlx = fxl[-1]
            scraper = cloudscraper.create_scraper(interpreter="nodejs", allow_brotli=False)
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
            }
            apix = "https://diskuploader.entertainvideo.com/v1/file/cdnurl?param={}".format(urlx)
            response = scraper.get(apix, headers=headers)
            query = response.json()
            return query
        except ValueError:
            textx = "The Content is Deleted."

@app.route('/')
def index():
    conn = get_db_connection()
    urls = conn.execute('SELECT * FROM urls').fetchall()
    conn.close()
    return render_template('index.html', urls=urls)

@app.route('/<int:url_id>')
def url(url_id):
    url = get_post(url_id)
    return render_template('url.html', url=url)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        link = request.form['title']

        if not link:
            flash('Link is required!')
        else:
            mdisk_json = get_video_url_from_mdisk(link)
            conn = get_db_connection()
            write_file(mdisk_json['filename'], mdisk_json['source'])
            conn.execute('INSERT INTO urls (filename, url) VALUES (?, ?)',
                         (mdisk_json['filename'], mdisk_json['source']))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

if __name__ == "__main__":
    app.run(debug=True)