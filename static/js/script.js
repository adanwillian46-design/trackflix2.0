console.log("✅ script.js carregado com sucesso!");

// Função de teste
function addMovie() {
    const title = document.getElementById('movieTitle').value;
    
    if (!title) {
        alert("Por favor, digite um título");
        return;
    }
    
    alert(`Tentando adicionar: ${title}`);
    
    // Dados de teste
    const movieData = {
        title: title,
        year: document.getElementById('movieYear').value,
        type: document.getElementById('movieType').value,
        genre: document.getElementById('movieGenre').value,
        poster: document.getElementById('moviePoster').value,
        notes: document.getElementById('movieNotes').value
    };
    
    console.log("Enviando dados:", movieData);
    
    // Teste da API
    fetch('/api/movies', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(movieData)
    })
    .then(response => {
        console.log("Status da resposta:", response.status);
        return response.json();
    })
    .then(data => {
        console.log("Resposta da API:", data);
        if (data.success) {
            alert("✅ Filme adicionado com sucesso!");
            location.reload(); // Recarrega a página
        } else {
            alert("❌ Erro: " + (data.error || "Erro desconhecido"));
        }
    })
    .catch(error => {
        console.error("Erro na requisição:", error);
        alert("❌ Erro de conexão com o servidor");
    });
}

// Funções simples para teste
function searchMovies() {
    const query = document.getElementById('searchInput').value;
    alert(`Buscando: ${query}`);
}

function filterMovies(status) {
    alert(`Filtrando por: ${status}`);
    // Atualiza botões ativos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Teste quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ Página carregada!");
    console.log("URL atual:", window.location.href);
    
    // Testa se os elementos existem
    console.log("Elementos encontrados:");
    console.log("- searchInput:", document.getElementById('searchInput'));
    console.log("- movieTitle:", document.getElementById('movieTitle'));
    console.log("- movieGrid:", document.getElementById('movieGrid'));
});