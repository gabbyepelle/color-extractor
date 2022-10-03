import webcolors
import seaborn as sns
from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory, send_file
import os
from werkzeug.utils import secure_filename
import pandas as pd
from colormap import rgb2hex
import colorgram
import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECTET_KEY'] = os.getenv('secret_key')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('process_image', name=filename))
    return render_template("index.html")


@app.route('/analysis/<name>')
def process_image(name):
    file = f'static/uploads/{name}'
    colors = colorgram.extract(file, 10)
    hex_list = []
    proportions = []
    for color in colors:
        hex_list.append(webcolors.rgb_to_hex(color.rgb))
        proportions.append(color.proportion)

    df = pd.DataFrame(zip(hex_list, proportions), columns=['Hex Code', 'Percentage'])
    sns.set()
    sns.palplot(hex_list, size=(3))
    ax = plt.gca()

    for i, j in enumerate(hex_list):
        ax.text(i, 0, j, fontsize=14, bbox=dict(facecolor='white', alpha=0.5))

    plt.savefig(f'static/uploads/pal-{name}')
    palette = f'pal-{name}'
    return render_template('analysis.html', table=[df.to_html(classes='data', index=False)], titles=df.columns.values,
                           name=name, palette=palette)


@app.route('/new')
def new_image():
    path = 'static/uploads'
    for file_name in os.listdir(path):
        # construct full file path
        file_object_path = os.path.join(path, file_name)
        if os.path.isfile(file_object_path):
            os.remove(file_object_path)
    return redirect(url_for('upload_file'))


if __name__ == '__main__':
    app.run(debug=True)
