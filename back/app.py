from flask import Flask, render_template
from back.controller.init_page import init_page_bp
from back.controller.partida_controller import partida_bp

app = Flask(__name__, template_folder='../Front', static_folder='../Front/static')

app.register_blueprint(init_page_bp)
app.register_blueprint(partida_bp)

@app.route('/')
def index():
    return render_template('index.html')