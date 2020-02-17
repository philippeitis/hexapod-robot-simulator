data = [
  {'name': 'body mesh',
   'showlegend': True,
   'type': 'mesh3d',
   'opacity': 0.3,
   'color': '#8e44ad',
   'uid': '1f821e07-2c02-4a64-8ce3-61ecfe2a91b6',
   'x': [100, 100, -100, -100, -100, 100, 100],
   'y': [0, 100, 100, 0, -100, -100, 0],
   'z': [0, 0, 0, 0, 0, 0, 0]},
  {'line': {'color': '#8e44ad', 'width': 10},
   'name': 'body',
   'showlegend': True,
   'type': 'scatter3d',
   'uid': '1f821e07-2c02-4a64-8ce3-61ecfe2a91b6',
   'x': [100, 100, -100, -100, -100, 100, 100],
   'y': [0, 100, 100, 0, -100, -100, 0],
   'z': [0, 0, 0, 0, 0, 0, 0]},
  {'marker': {'color': '#e74c3c', 'opacity': 1.0, 'size': 10},
   'mode': 'markers',
   'name': 'cog',
   'type': 'scatter3d',
   'uid': 'a819d0e4-ddaa-476b-b3e4-48fd766e749c',
   'x': [0],
   'y': [0],
   'z': [0]},
  {'marker': {'color': '#8e44ad', 'opacity': 1.0, 'size': 15},
   'mode': 'markers',
   'name': 'head',
   'type': 'scatter3d',
   'uid': '508caa99-c538-4cb6-b022-fbbb31c2350b',
   'x': [0],
   'y': [100],
   'z': [0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': 'f217db57-fe6e-4b40-90f8-4e1c20ef595e',
   'x': [100, 200.0, 300.0, 300.0],
   'y': [0, 0.0, 0.0, 0.0],
   'z': [0, 0.0, 0.0, -100.0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': 'd5690122-cd54-460d-ab3e-1f910eb88f0f',
   'x': [100, 170.71067811865476, 241.4213562373095, 241.4213562373095],
   'y': [100, 170.71067811865476, 241.42135623730948, 241.42135623730948],
   'z': [0, 0.0, 0.0, -100.0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': '9f13f416-f2b7-4eb7-993c-1e26e2e7a908',
   'x': [-100, -170.71067811865476, -241.42135623730948, -241.42135623730948],
   'y': [100, 170.71067811865476, 241.4213562373095, 241.4213562373095],
   'z': [0, 0.0, 0.0, -100.0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': '0d426c49-19a4-4051-b938-81b30c962dff',
   'x': [-100, -200.0, -300.0, -300.0],
   'y': [0, 1.2246467991473532e-14, 2.4492935982947064e-14, 2.4492935982947064e-14],
   'z': [0, 0.0, 0.0, -100.0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': '5ba25594-2fb5-407e-a16f-118f12769e28',
   'x': [-100, -170.71067811865476, -241.42135623730954, -241.42135623730954],
   'y': [-100, -170.71067811865476, -241.42135623730948, -241.42135623730948],
   'z': [0, 0.0, 0.0, -100.0]},
  {'line': {'color': '#2c3e50', 'width': 10},
   'name': 'leg',
   'showlegend': False,
   'type': 'scatter3d',
   'uid': 'fa4b5f98-7d68-4eb9-bd38-a6f8dabef8a4',
   'x': [100, 170.71067811865476, 241.42135623730948, 241.42135623730948],
   'y': [-100, -170.71067811865476, -241.42135623730954, -241.42135623730954],
   'z': [0, 0.0, 0.0, -100.0]},
]

HEXAPOD_FIGURE = {
  'data': data,
  'layout': {
    'hovermode': 'closest', #'hoverdistance': 1000 doesn't look like it's going anything
    'legend': {'x': 0, 'y': 0},
    'margin': {'b': 20, 'l': 10, 'r': 10, 't': 20},
    'scene': {
      'aspectmode': 'manual',
      'aspectratio': {'x': 1, 'y': 1, 'z': 1},
      'camera': {
        'center': {'x': -0.05, 'y': 0, 'z': -0.1},
        'eye': {'x': 0.35, 'y': 0.7, 'z': 0.48999999999999994},
        'up': {'x': 0, 'y': 0, 'z': 1}
      },
      'xaxis': {'nticks': 1, 'range': [-600, 600], 'showbackground': False},
      'yaxis': {'nticks': 1, 'range': [-600, 600], 'showbackground': False},
      'zaxis': {'nticks': 1, 'range': [-600, 600], 'showbackground': True, 'backgroundcolor': 'rgb(230, 230, 2005)'}
    },
    'template': '...'
  }
}