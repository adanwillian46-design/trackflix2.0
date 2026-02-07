from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from datetime import datetime

app = Flask(__name__)

# Arquivo para armazenar os filmes
MOVIES_FILE = 'movies.json'

def load_movies():
    """Carrega os filmes do arquivo JSON"""
    if os.path.exists(MOVIES_FILE):
        try:
            with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Erro ao carregar filmes: {e}")
            return []
    return []

def save_movies(movies):
    """Salva os filmes no arquivo JSON"""
    try:
        with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(movies, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar filmes: {e}")
        return False

@app.route('/')
def index():
    """Página principal"""
    movies = load_movies()
    print(f"🎬 Carregando {len(movies)} filmes para a página inicial")
    return render_template('index.html', movies=movies)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/test')
def test_api():
    """Teste da API"""
    movies = load_movies()
    return jsonify({
        'status': 'ok',
        'message': 'API Trackflix funcionando!',
        'movies_count': len(movies),
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/movies', methods=['GET'])
def get_all_movies():
    """Retorna todos os filmes"""
    movies = load_movies()
    return jsonify(movies)

@app.route('/api/movies', methods=['POST'])
def add_movie():
    """Adiciona um novo filme"""
    try:
        data = request.json
        print(f"📥 Recebendo dados para novo filme: {data}")
        
        if not data or not data.get('title'):
            return jsonify({
                'success': False, 
                'error': 'Título é obrigatório'
            }), 400
        
        movies = load_movies()
        
        # Cria um novo ID
        new_id = max([m.get('id', 0) for m in movies], default=0) + 1
        
        new_movie = {
            'id': new_id,
            'title': data.get('title', '').strip(),
            'year': data.get('year', '').strip(),
            'type': data.get('type', 'movie'),
            'poster': data.get('poster', '').strip(),
            'genre': data.get('genre', '').strip(),
            'status': data.get('status', 'pending'),
            'rating': data.get('rating', 0),
            'notes': data.get('notes', '').strip(),
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        movies.append(new_movie)
        
        if save_movies(movies):
            print(f"✅ Filme adicionado com sucesso: {new_movie['title']} (ID: {new_movie['id']})")
            return jsonify({
                'success': True, 
                'movie': new_movie
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Erro ao salvar no arquivo'
            }), 500
        
    except Exception as e:
        print(f"❌ Erro ao adicionar filme: {e}")
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/movies/<int:movie_id>/rating', methods=['PUT'])
def update_rating(movie_id):
    """Atualiza a avaliação de um filme"""
    try:
        data = request.json
        rating = data.get('rating', 0)
        
        movies = load_movies()
        
        for movie in movies:
            if movie.get('id') == movie_id:
                movie['rating'] = rating
                movie['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if save_movies(movies):
                    return jsonify({
                        'success': True, 
                        'rating': rating
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'Erro ao salvar'
                    }), 500
        
        return jsonify({
            'success': False, 
            'error': 'Filme não encontrado'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/movies/<int:movie_id>/status', methods=['PUT'])
def update_status(movie_id):
    """Atualiza o status de um filme"""
    try:
        data = request.json
        status = data.get('status', 'pending')
        
        movies = load_movies()
        
        for movie in movies:
            if movie.get('id') == movie_id:
                movie['status'] = status
                
                if save_movies(movies):
                    return jsonify({
                        'success': True, 
                        'status': status
                    })
                else:
                    return jsonify({
                        'success': False, 
                        'error': 'Erro ao salvar'
                    }), 500
        
        return jsonify({
            'success': False, 
            'error': 'Filme não encontrado'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    """Remove um filme"""
    try:
        movies = load_movies()
        initial_count = len(movies)
        
        movies = [m for m in movies if m.get('id') != movie_id]
        
        if len(movies) < initial_count:
            if save_movies(movies):
                return jsonify({'success': True})
            else:
                return jsonify({
                    'success': False, 
                    'error': 'Erro ao salvar'
                }), 500
        else:
            return jsonify({
                'success': False, 
                'error': 'Filme não encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        }), 500

@app.route('/api/search', methods=['GET'])
def search_movies():
    """Busca filmes por título ou gênero"""
    try:
        query = request.args.get('q', '').lower()
        movies = load_movies()
        
        if query:
            filtered = [
                m for m in movies 
                if query in m.get('title', '').lower() or 
                   query in m.get('genre', '').lower() or
                   query in m.get('year', '')
            ]
        else:
            filtered = movies
        
        return jsonify(filtered)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# PÁGINAS DE DIAGNÓSTICO E DEBUG
# ============================================

@app.route('/debug')
def debug():
    """Página de diagnóstico do sistema"""
    
    # Coletar informações do sistema
    system_info = {
        'working_directory': os.getcwd(),
        'python_version': sys.version,
        'flask_imported': True,
        'files': {
            'movies_json': {
                'exists': os.path.exists(MOVIES_FILE),
                'path': os.path.abspath(MOVIES_FILE) if os.path.exists(MOVIES_FILE) else 'Não existe',
                'size': os.path.getsize(MOVIES_FILE) if os.path.exists(MOVIES_FILE) else 0
            },
            'templates_folder': {
                'exists': os.path.exists('templates'),
                'files': os.listdir('templates') if os.path.exists('templates') else []
            },
            'static_folder': {
                'exists': os.path.exists('static'),
                'css_exists': os.path.exists('static/css'),
                'js_exists': os.path.exists('static/js')
            }
        },
        'movies_data': {
            'count': len(load_movies()),
            'sample': load_movies()[:3]  # Primeiros 3 filmes para exemplo
        }
    }
    
    # Gerar HTML da página de debug
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🔧 Debug - Trackflix</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0c29, #302b63);
                color: #ffffff;
                min-height: 100vh;
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            header {{
                text-align: center;
                padding: 30px 0;
                margin-bottom: 30px;
            }}
            
            h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(90deg, #00dbde, #fc00ff);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }}
            
            h2 {{
                color: #8a8aff;
                margin: 25px 0 15px 0;
                padding-bottom: 10px;
                border-bottom: 2px solid rgba(138, 138, 255, 0.3);
            }}
            
            .card {{
                background: rgba(26, 26, 46, 0.8);
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .status {{
                display: inline-block;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin: 5px;
            }}
            
            .status-ok {{
                background: rgba(0, 255, 0, 0.2);
                color: #00ff00;
            }}
            
            .status-error {{
                background: rgba(255, 0, 0, 0.2);
                color: #ff4444;
            }}
            
            .status-warning {{
                background: rgba(255, 165, 0, 0.2);
                color: #ffa500;
            }}
            
            pre {{
                background: rgba(0, 0, 0, 0.3);
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                font-family: 'Courier New', monospace;
                font-size: 0.9rem;
                margin: 10px 0;
            }}
            
            .buttons {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 20px 0;
            }}
            
            button {{
                padding: 12px 25px;
                background: linear-gradient(90deg, #00dbde, #fc00ff);
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 600;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            
            button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            
            .test-btn {{
                background: rgba(0, 219, 222, 0.2);
                border: 1px solid rgba(0, 219, 222, 0.3);
            }}
            
            .add-btn {{
                background: rgba(0, 176, 155, 0.2);
                border: 1px solid rgba(0, 176, 155, 0.3);
            }}
            
            .list-btn {{
                background: rgba(138, 138, 255, 0.2);
                border: 1px solid rgba(138, 138, 255, 0.3);
            }}
            
            #result {{
                margin-top: 20px;
                min-height: 100px;
            }}
            
            .result-box {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                padding: 15px;
                margin-top: 10px;
                border-left: 4px solid #00dbde;
            }}
            
            .success {{
                border-left-color: #00ff00;
                color: #00ff00;
            }}
            
            .error {{
                border-left-color: #ff4444;
                color: #ff4444;
            }}
            
            .info {{
                border-left-color: #44aaff;
                color: #44aaff;
            }}
            
            .file-list {{
                list-style: none;
                padding-left: 20px;
            }}
            
            .file-list li {{
                padding: 5px 0;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .file-list li::before {{
                content: "📄";
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔧 Diagnóstico Trackflix</h1>
                <p>Verifique o status do sistema e teste as funcionalidades</p>
            </header>
            
            <div class="card">
                <h2>📊 Status do Sistema</h2>
                
                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px;">
                    <span class="status status-ok">Python {system_info['python_version'].split()[0]}</span>
                    <span class="status status-ok">Flask Instalado</span>
                    <span class="status { 'status-ok' if system_info['files']['movies_json']['exists'] else 'status-error' }">
                        Arquivo movies.json: { '✅' if system_info['files']['movies_json']['exists'] else '❌' }
                    </span>
                    <span class="status { 'status-ok' if system_info['files']['templates_folder']['exists'] else 'status-error' }">
                        Pasta templates: { '✅' if system_info['files']['templates_folder']['exists'] else '❌' }
                    </span>
                    <span class="status { 'status-ok' if system_info['files']['static_folder']['exists'] else 'status-warning' }">
                        Pasta static: { '✅' if system_info['files']['static_folder']['exists'] else '⚠️' }
                    </span>
                </div>
                
                <h3>📁 Estrutura de Arquivos:</h3>
                <pre>{json.dumps(system_info['files'], indent=2)}</pre>
                
                <h3>🎬 Dados dos Filmes:</h3>
                <p>Total de filmes cadastrados: <strong>{system_info['movies_data']['count']}</strong></p>
                <pre>{json.dumps(system_info['movies_data']['sample'], indent=2)}</pre>
            </div>
            
            <div class="card">
                <h2>🧪 Testes da API</h2>
                <p>Clique nos botões abaixo para testar as funcionalidades da API:</p>
                
                <div class="buttons">
                    <button class="test-btn" onclick="testAPI()">
                        <span>🔧</span> Testar API
                    </button>
                    <button class="add-btn" onclick="testAddMovie()">
                        <span>➕</span> Adicionar Filme Teste
                    </button>
                    <button class="list-btn" onclick="testListMovies()">
                        <span>📋</span> Listar Filmes
                    </button>
                    <button onclick="testSearch()">
                        <span>🔍</span> Testar Busca
                    </button>
                    <button onclick="goToHome()">
                        <span>🏠</span> Ir para Home
                    </button>
                </div>
                
                <div id="result">
                    <!-- Resultados aparecerão aqui -->
                </div>
            </div>
            
            <div class="card">
                <h2>📋 Logs do Servidor</h2>
                <div id="logs">
                    <p>Os logs do servidor aparecerão aqui quando você executar os testes.</p>
                </div>
            </div>
        </div>
        
        <script>
        function showResult(message, type = 'info') {{
            const resultDiv = document.getElementById('result');
            const div = document.createElement('div');
            div.className = `result-box ${{type}}`;
            div.innerHTML = `<pre>${{message}}</pre>`;
            resultDiv.appendChild(div);
            div.scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        function clearResults() {{
            document.getElementById('result').innerHTML = '';
        }}
        
        function addLog(message) {{
            const logsDiv = document.getElementById('logs');
            const p = document.createElement('p');
            p.textContent = `[${{new Date().toLocaleTimeString()}}] ${{message}}`;
            logsDiv.appendChild(p);
        }}
        
        async function testAPI() {{
            clearResults();
            addLog('Testando API...');
            showResult('⏳ Testando conexão com a API...', 'info');
            
            try {{
                const startTime = Date.now();
                const response = await fetch('/api/test');
                const endTime = Date.now();
                const data = await response.json();
                
                const resultText = `✅ API Funcionando!
Tempo de resposta: ${{endTime - startTime}}ms
Status: ${{data.status}}
Mensagem: ${{data.message}}
Total de filmes: ${{data.movies_count}}
Timestamp: ${{data.timestamp}}`;
                
                showResult(resultText, 'success');
                addLog('✅ API testada com sucesso');
            }} catch (error) {{
                showResult(`❌ Erro ao testar API:\\n${{error}}`, 'error');
                addLog(`❌ Erro na API: ${{error}}`);
            }}
        }}
        
        async function testAddMovie() {{
            clearResults();
            addLog('Adicionando filme teste...');
            showResult('⏳ Adicionando filme de teste...', 'info');
            
            const movieData = {{
                title: "Filme Teste " + new Date().toLocaleTimeString(),
                year: "2024",
                type: "movie",
                genre: "Ação",
                notes: "Este é um filme de teste criado pela página de debug"
            }};
            
            try {{
                const response = await fetch('/api/movies', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify(movieData)
                }});
                
                const data = await response.json();
                
                if (data.success) {{
                    const resultText = `✅ Filme adicionado com sucesso!
ID: ${{data.movie.id}}
Título: ${{data.movie.title}}
Tipo: ${{data.movie.type}}
Data: ${{data.movie.date_added}}`;
                    
                    showResult(resultText, 'success');
                    addLog(`✅ Filme "${{data.movie.title}}" adicionado com sucesso`);
                }} else {{
                    showResult(`❌ Erro ao adicionar filme:\\n${{data.error}}`, 'error');
                    addLog(`❌ Erro ao adicionar filme: ${{data.error}}`);
                }}
            }} catch (error) {{
                showResult(`❌ Erro de conexão:\\n${{error}}`, 'error');
                addLog(`❌ Erro de conexão: ${{error}}`);
            }}
        }}
        
        async function testListMovies() {{
            clearResults();
            addLog('Listando filmes...');
            showResult('⏳ Buscando lista de filmes...', 'info');
            
            try {{
                const response = await fetch('/api/search?q=');
                const movies = await response.json();
                
                if (movies.length > 0) {{
                    const resultText = `✅ Encontrados ${{movies.length}} filmes:

${{JSON.stringify(movies, null, 2)}}`;
                    
                    showResult(resultText, 'info');
                    addLog(`✅ Listados ${{movies.length}} filmes`);
                }} else {{
                    showResult('ℹ️ Nenhum filme encontrado. Adicione um filme primeiro.', 'info');
                    addLog('ℹ️ Nenhum filme cadastrado');
                }}
            }} catch (error) {{
                showResult(`❌ Erro ao listar filmes:\\n${{error}}`, 'error');
                addLog(`❌ Erro ao listar filmes: ${{error}}`);
            }}
        }}
        
        async function testSearch() {{
            clearResults();
            addLog('Testando busca...');
            showResult('⏳ Testando funcionalidade de busca...', 'info');
            
            try {{
                const response = await fetch('/api/search?q=teste');
                const movies = await response.json();
                
                showResult(`✅ Busca por "teste" retornou ${{movies.length}} resultados`, 'info');
                addLog(`✅ Busca testada com ${{movies.length}} resultados`);
            }} catch (error) {{
                showResult(`❌ Erro na busca:\\n${{error}}`, 'error');
                addLog(`❌ Erro na busca: ${{error}}`);
            }}
        }}
        
        function goToHome() {{
            window.location.href = '/';
        }}
        
        // Teste inicial automático
        document.addEventListener('DOMContentLoaded', function() {{
            addLog('Página de debug carregada');
            addLog('Sistema pronto para testes');
        }});
        </script>
    </body>
    </html>
    '''
    
    return html

@app.route('/quick-test')
def quick_test():
    """Página de teste rápido"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Teste Rápido</title>
        <style>
            body { background: #0f0c29; color: white; padding: 20px; }
            button { padding: 10px 20px; margin: 5px; background: #00dbde; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Teste Rápido API</h1>
        <button onclick="test()">Testar</button>
        <div id="result"></div>
        <script>
        async function test() {
            try {
                const res = await fetch('/api/test');
                const data = await res.json();
                document.getElementById('result').innerHTML = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('result').innerHTML = "Erro: " + e;
            }
        }
        </script>
    </body>
    </html>
    '''

# ============================================
# INICIALIZAÇÃO DO SERVIDOR
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 INICIANDO TRACKFLIX - SISTEMA DE GERENCIAMENTO")
    print("=" * 60)
    print(f"📂 Diretório atual: {os.getcwd()}")
    print(f"📁 Arquivo de dados: {os.path.abspath(MOVIES_FILE)}")
    print(f"   • Existe: {os.path.exists(MOVIES_FILE)}")
    if os.path.exists(MOVIES_FILE):
        movies = load_movies()
        print(f"   • Filmes cadastrados: {len(movies)}")
    
    print(f"📁 Pasta templates: {os.path.exists('templates')}")
    if os.path.exists('templates'):
        print(f"   • Arquivos: {os.listdir('templates')}")
    
    print(f"📁 Pasta static: {os.path.exists('static')}")
    print(f"🔧 Modo debug: ATIVADO")
    print("=" * 60)
    print("🌐 URLs disponíveis:")
    print("   • http://localhost:5000/ - Página principal")
    print("   • http://localhost:5000/debug - Página de diagnóstico")
    print("   • http://localhost:5000/quick-test - Teste rápido")
    print("   • http://localhost:5000/api/test - Teste da API")
    print("   • http://localhost:5000/api/movies - Listar filmes (GET)")
    print("=" * 60)
    print("🔄 Pressione CTRL+C para parar o servidor")
    print("=" * 60)
    
    try:
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        print("💡 Verifique se a porta 5000 não está em uso")