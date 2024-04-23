from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response
from flask_caching import Cache
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objs as go

app = Flask(__name__)
app.secret_key = "clave_secreta"  
cache = Cache(app, config={'CACHE_TYPE': 'simple'})



def esta_autenticado():
    return 'usuario' in session


@app.before_request
def requerir_autenticacion():
    if not esta_autenticado() and request.endpoint != 'login' and not request.path.startswith('/static'):
        return redirect(url_for('login'))

@app.route('/')
def inicio():
    if esta_autenticado():
        return redirect(url_for('mostrar_grafico'))
    else:
         
        response = make_response(render_template('Login.html'))
       
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    



def conector():
    engine = create_engine("mysql+mysqlconnector://limacinv:D%j9Uf?B*@tuticketlimac.com/limac_prod")
    return engine


def obtener_general():
    engine = conector()
    query = "SELECT * FROM ticket"
    df = pd.read_sql_query(query, engine)
    return df

def obtener_datos_filtrados(fecha_inicio, fecha_fin, tipo_ticket):
   
    engine = conector()

   
    query = f"SELECT * FROM ticket WHERE start_date BETWEEN '{fecha_inicio}' AND '{fecha_fin}'"
    if tipo_ticket:
        query += f" AND ref = '{tipo_ticket}'"
    
   
    df = pd.read_sql_query(query, engine)
    
    return df



def liss():
    engine = conector()
    query = "SELECT * FROM priv_user"
    lj = pd.read_sql_query(query,engine)
    return lj


def obtener_incidente():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 25"
    di = pd.read_sql_query(query,engine)
    return di


def obtener_cdn1():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 31"
    encli = pd.read_sql_query(query,engine)
    return encli


def obtener_gdln1():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 26"
    jam = pd.read_sql_query(query,engine)
    return jam

 
def obtener_gdln2():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 32"
    rl = pd.read_sql_query(query,engine)
    return rl


def obtener_ln1():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 27"
    ln = pd.read_sql_query(query,engine)
    return ln

def obtener_ln2():
    engine = conector()
    query = "SELECT * FROM ticket WHERE team_id = 33"
    lns = pd.read_sql_query(query,engine)
    return lns



@cache.cached(timeout=300) 
def obtener_general_cached():
    return obtener_general()


@cache.cached(timeout=300)  
def obtener_grafico_barras_cached():

    response = obtener_grafico_barras()
    return response

def verificar_credenciales(usuario, contraseña):
    usuarios = liss()  
    usuario = int(usuario)
    if usuarios[(usuarios['id'] == usuario) & (usuarios['login'] == contraseña)].shape[0] > 0:
    
        return True

    return False


@app.route('/templates/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form)  
        usuario = request.form.get('id')  
        contraseña = request.form.get('login') 
        if verificar_credenciales(usuario, contraseña):
            session['usuario'] = usuario
            return redirect(url_for('mostrar_grafico'))  
        else:
            return render_template('Login.html', error=True)
    return render_template('Login.html', error=False) 



@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('inicio'))


@app.route('/tickets')
def mostrar_grafico():
    df = obtener_general_cached()  
    conteo_por_estado = df['operational_status'].value_counts()
    labels = conteo_por_estado.index.tolist()
    valores = conteo_por_estado.values.tolist()
    grafico_pastel = go.Pie(labels=labels, values=valores)
    layout = go.Layout(title='Gráfico de pastel',)
    fig = go.Figure(data=[grafico_pastel], layout=layout)
    graphJSON = fig.to_json()


    response = obtener_grafico_barras()  
    graphJSON_barras = response.json  
    
    return render_template('tickets.html', graphJSON=graphJSON, graphJSON_barras=graphJSON_barras)



@app.route('/obtener_grafico_barras', methods=['GET'])
def obtener_grafico_barras():
    df = obtener_general() 
    conteo_por_estado = df['operational_status'].value_counts()  
    labels = conteo_por_estado.index.tolist()  
    valores = conteo_por_estado.values.tolist()  
    grafico_barras = go.Bar(x=labels, y=valores)
    layout_barras = go.Layout(title='Gráfico de barras')
    fig_barras = go.Figure(data=[grafico_barras], layout=layout_barras)
    graphJSON_barras = fig_barras.to_json() 
    return jsonify({'graphJSON_barras': graphJSON_barras})


@app.route('/actualizar_grafico', methods=['POST'])
def actualizar_grafico():
    fecha_inicio = request.json['fecha_inicio']
    fecha_fin = request.json['fecha_fin']
    team_id = request.json.get('team_id')  
    tipo_ticket = request.json.get('ref')
    
    if fecha_inicio == fecha_fin: 
        return jsonify({"error": "Las fechas de inicio y fin no pueden ser iguales"})
    
    df = obtener_general()
    df['start_date'] = pd.to_datetime(df['start_date']) 
    df_filtrado = df[(df['start_date'] >= pd.to_datetime(fecha_inicio)) & (df['start_date'] <= pd.to_datetime(fecha_fin))]
    if team_id:  
        df_filtrado = df_filtrado[df_filtrado['team_id'] == int(team_id)]  
    
 
    if tipo_ticket == 'I':
        df_filtrado = df_filtrado[df_filtrado['ref'].str.startswith('I')]
    elif tipo_ticket == 'R':
        df_filtrado = df_filtrado[df_filtrado['ref'].str.startswith('R')]
    
   
    conteo_por_estado = df_filtrado['operational_status'].value_counts()
    labels = conteo_por_estado.index.tolist()
    valores = conteo_por_estado.values.tolist()
    
  
    grafico_pastel = go.Pie(labels=labels, values=valores)
    layout_pastel = go.Layout(title='Gráfico de pastel filtrado por rango de Fechas y Sucursal')
    fig_pastel = go.Figure(data=[grafico_pastel], layout=layout_pastel)
    graphJSON_pastel = fig_pastel.to_json()
    

    grafico_barras = go.Bar(x=labels, y=valores)
    layout_barras = go.Layout(title='Gráfico de barras filtrado por rango de Fechas y Sucursal')
    fig_barras = go.Figure(data=[grafico_barras], layout=layout_barras)
    graphJSON_barras = fig_barras.to_json()
    
    return jsonify({'graphJSON_pastel': graphJSON_pastel, 'graphJSON_barras': graphJSON_barras})


#Comienza funcion e implementación de incidentes

@app.route('/requerimientos')
def requer():
    return render_template('requerimientos.html')

@app.route('/sucursal')
def indexsucursal():
    return render_template('sucursal.html')

@app.route('/gdl')
def chivas():
    return render_template('gdl.html')




if __name__ == '__main__':
    app.run(debug=False)