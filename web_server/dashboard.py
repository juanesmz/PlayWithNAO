import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def Dashboard():
    # Cargar y limpiar datos
    df = pd.read_csv('assets/data.csv', dayfirst=True)
    df.replace('NA', pd.NA, inplace=True)
    df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)

    colores = df.columns[3:]  # columnas de colores
    ids = df['ID'].dropna().unique()

    # Inicializar app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Función para calcular puntaje
    def calcular_puntaje(grupo):
        puntos = 0
        total = 0
        for _, row in grupo.iterrows():
            for color in colores:
                val = row[color]
                if val == 'Correcta':
                    puntos += 1
                    total += 1
                elif val == 'Incorrecta':
                    puntos += 0.5
                    total += 1
        return (puntos / total * 100) if total > 0 else 0

    # Layout
    app.layout = dbc.Container([
        # Encabezado con logos
        dbc.Row([
            dbc.Col(html.Img(src='assets/logo_final.png', height='60px'), width=3, className="d-flex align-items-center"),
            dbc.Col(html.H2("Análisis de Actividades", className="text-center m-0"), width=6, className="d-flex align-items-center justify-content-center"),
            dbc.Col(html.Img(src='assets/logo_capsab.png', height='60px'), width=1, className="d-flex align-items-center justify-content-end"),
            dbc.Col(html.Img(src='assets/logo_unisabana.png', height='60px'), width=2, className="d-flex align-items-center justify-content-end")
        ], className="mb-4", style={"backgroundColor": "#e9ecef", "padding": "10px", "borderRadius": "8px"}),

        # Filtros en card
        dbc.Card([
            dbc.CardHeader("Aplique sus filtros", className="fw-bold"),
            dbc.CardBody(
                dbc.Row([
                    dbc.Col(
                        className="d-flex align-items-center justify-content-center", 
                        width=5,
                        children=html.Div(
                            dcc.Dropdown(
                                id='id-dropdown',
                                options=[{'label': i, 'value': i} for i in ids],
                                placeholder="Seleccione un ID",
                                style={'height': '40px'}
                            ),
                            style={'width': '75%'}  # Puedes cambiar a '75%' o '250px' si quieres un ancho más controlado
                        )
                    ),

                    dbc.Col([
                        html.Label("Seleccione fechas:", className="mb-1 text-end")], className="d-flex align-items-center justify-content-end", width=2),
                        
                    dbc.Col([
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=df['Fecha'].min(),
                            max_date_allowed=df['Fecha'].max(),
                            start_date=df['Fecha'].min(),
                            end_date=df['Fecha'].max(),
                            style={'height': '40px'}
                        )
                    ], width=5)
                ])
            )
        ], className="mb-4 shadow"),

        # Cards
        dbc.Row([
            dbc.Col(dbc.Card([dbc.CardHeader("Total de actividades"),
                            dbc.CardBody(id="total-card-body")], className="mb-4 shadow"), width=6),
            dbc.Col(dbc.Card([dbc.CardHeader("Puntaje ponderado"),
                            dbc.CardBody(id="puntaje-card-body")], className="mb-4 shadow"), width=6)
        ], className="mb-4"),

        # Gráfico 1: respuestas por color
        dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Respuestas por color"),
                        dbc.CardBody(dcc.Graph(id='grafico-colores',
                                            config={'displayModeBar': False}
                                            ))
                    ], className="mb-4 shadow"),
                    width=6
                ),
            
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Puntaje y actividades por fecha"),
                        dbc.CardBody(dcc.Graph(id='grafico-fechas',
                                            config={'displayModeBar': False}))
                    ], className="mb-4 shadow"),
                    width=6
                )
        ], className="mb-4")
    ], fluid=True)

    # Callback
    @callback(
        [Output('total-card-body', 'children'),
        Output('puntaje-card-body', 'children'),
        Output('grafico-colores', 'figure'),
        Output('grafico-fechas', 'figure')],
        [Input('id-dropdown', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date')]
    )
    def actualizar_dashboard(selected_id, start_date, end_date):
        df_filtrado = df.copy()

        if selected_id:
            df_filtrado = df_filtrado[df_filtrado['ID'] == selected_id]

        if start_date and end_date:
            df_filtrado = df_filtrado[
                (df_filtrado['Fecha'] >= pd.to_datetime(start_date)) &
                (df_filtrado['Fecha'] <= pd.to_datetime(end_date))
            ]

        # Cards
        card_total = f"{len(df_filtrado)}"
        card_puntaje = f"{calcular_puntaje(df_filtrado):.2f}%"

        # Gráfico 1: Respuestas por color
        melted = df_filtrado.melt(id_vars=['ID'], value_vars=colores,
                                var_name='Color', value_name='Respuesta').dropna()
        respuesta = []
        for color in melted['Color'].unique():
            respuesta.append({'Color':color,
                            'Correctas':len(melted[(melted['Color']==color) & (melted['Respuesta']=='Correcta')]),
                            'Incorrectas':len(melted[(melted['Color']==color) & (melted['Respuesta']=='Incorrecta')])})

        grouped_df = pd.DataFrame(respuesta)
        
        fig1 = go.Figure()

        # Barra de actividades (eje primario izquierdo)
        fig1.add_trace(go.Bar(
            x=grouped_df['Color'],
            y=grouped_df['Correctas'],
            name='Correctas',
            offsetgroup=1,
            marker_color='steelblue'
        ))

        # Barra de puntaje (eje secundario derecho)
        fig1.add_trace(go.Bar(
            x=grouped_df['Color'],
            y=grouped_df['Incorrectas'],
            name='Incorrectas',
            offsetgroup=2,
            marker_color='darkorange'
        ))

        # Configurar diseño de doble eje
        fig1.update_layout(
            xaxis=dict(title='Fecha'),
            yaxis=dict(
                title='Número de actividades',
                side='left',
                showgrid=False
            ),
            barmode='group',
            legend=dict(x=0.8, y=-0.25),
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="#ffffff",     # fondo del área de trazado
            paper_bgcolor="#ffffff",    # fondo del área general
            font=dict(color="black"),
        )

        # Gráfico 2: Puntaje y actividades por fecha
        resumen = []
        for fecha, grupo in df_filtrado.groupby('Fecha'):
            resumen.append({
                'Fecha': fecha,
                'Actividades': len(grupo),
                'Puntaje': calcular_puntaje(grupo)
            })
        grouped_df = pd.DataFrame(resumen)

        # Crear figura con dos ejes
        fig2 = go.Figure()

        # Barra de actividades (eje primario izquierdo)
        fig2.add_trace(go.Bar(
            x=grouped_df['Fecha'],
            y=grouped_df['Actividades'],
            name='Actividades',
            yaxis='y1',
            offsetgroup=1,
            marker_color='steelblue'
        ))

        # Barra de puntaje (eje secundario derecho)
        fig2.add_trace(go.Bar(
            x=grouped_df['Fecha'],
            y=grouped_df['Puntaje'],
            name='Puntaje (%)',
            yaxis='y2',
            offsetgroup=2,
            marker_color='darkorange'
        ))

        # Configurar diseño de doble eje
        fig2.update_layout(
            xaxis=dict(title='Fecha'),
            yaxis=dict(
                title='Número de actividades',
                side='left',
                showgrid=False
            ),
            yaxis2=dict(
                title='Puntaje (%)',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[0, 100]  # porque es porcentaje
            ),
            barmode='group',
            legend=dict(x=0.8, y=-0.2),
            margin=dict(l=0, r=0, t=0, b=0),
            plot_bgcolor="#ffffff",     # fondo del área de trazado
            paper_bgcolor="#ffffff",    # fondo del área general
            font=dict(color="black"),
        )

        return card_total, card_puntaje, fig1, fig2
    return app


