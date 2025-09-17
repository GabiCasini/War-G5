from flask import Flask, render_template
from controller.init_page import init_page_bp

app = Flask(__name__)
app.register_blueprint(init_page_bp)

@app.route('/')
def index():
    return render_template('index.html')