# -*- coding: utf-8 -*-
import os,sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])
message="投稿がありません"


img_files=['/uploads/'+f for f in os.listdir("./uploads")]



#ページ変移
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/page1')
def home1():
    return render_template('page1.html',img_files=img_files)

@app.route('/page2')
def home2():
    return render_template('page2.html')









#page1
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        img_file = request.files['img_file']
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
            img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            img_url = '/uploads/' + filename
            img_files.append(img_url)
            return render_template('page1.html',img_files=img_files)
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        return redirect(url_for('page1'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



@app.route('/img', methods=['GET', 'POST'])
def img():
    if request.method == 'POST':
        rows=[]
        counter= int(request.form['counter'])
        img_url=img_files[counter-1]

        conn=sqlite3.connect('database.db')
        conn.row_factory=sqlite3.Row
        cur=conn.cursor()
        string="SELECT * FROM urltext WHERE url = \'"+img_url+"\'"
        cur.execute(string)
        rows=cur.fetchall()
        conn.close()  

        text=""
        for row in rows: 
            text=row["body"]
        return render_template('page2.html',img_url=img_url,text=text)
    else:
        return redirect(url_for('page2'))


         





#page2 
@app.route('/sql', methods=['GET', 'POST'])
def sql():
    if request.method == 'POST':
        # リクエストフォームから「名前」を取得して
        text = request.form['text']
        img_url=request.form['url']
        #sql table 作る
        conn=sqlite3.connect('database.db')
        cur=conn.cursor()
        cur.execute("INSERT OR REPLACE INTO urltext (url,body) VALUES(?,?)",(img_url,text))
        conn.commit()    
        conn.close()    
        return render_template('page2.html',img_url=img_url,text=text)
    else:
                # エラーなどでリダイレクトしたい場合はこんな感じで
        return redirect(url_for('page2'))


#main
def main():
    conn=sqlite3.connect('database.db')
    cur=conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS urltext (url TEXT PRIMARY KEY, body TEXT NOT NULL)")
    conn.close() 
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
    



if __name__ == '__main__':
    main()