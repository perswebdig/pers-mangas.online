/**
 * MangaDex PT - Cliente da API
 */

const API = {
    // URLs base
    BASE_URL: window.location.origin + '/api',
    MANGADEX_URL: window.location.origin + '/api/mangadex',
    
    // Métodos para mangás
    async obterPopulares(limit = 30, offset = 0) {
        return apiCall(`${this.MANGADEX_URL}/populares?limit=${limit}&offset=${offset}`);
    },
    
    async buscar(query, limit = 20, offset = 0) {
        if (!query || query.length < 2) {
            throw new Error('Query deve ter pelo menos 2 caracteres');
        }
        return apiCall(`${this.MANGADEX_URL}/buscar?q=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`);
    },
    
    async obterDetalhes(mangaId) {
        return apiCall(`${this.MANGADEX_URL}/manga/${mangaId}`);
    },
    
    async obterCapitulos(mangaId, limit = 1000, offset = 0) {
        return apiCall(`${this.MANGADEX_URL}/manga/${mangaId}/capitulos?limit=${limit}&offset=${offset}`);
    },
    
    async obterCategorias() {
        return apiCall(`${this.MANGADEX_URL}/categorias`);
    },
    
    async filtrar(filtros = {}) {
        const params = new URLSearchParams();
        if (filtros.status) params.append('status', filtros.status);
        if (filtros.demographic) params.append('demographic', filtros.demographic);
        if (filtros.tags) params.append('tags', filtros.tags);
        if (filtros.limit) params.append('limit', filtros.limit);
        if (filtros.offset) params.append('offset', filtros.offset);
        
        return apiCall(`${this.MANGADEX_URL}/filtrar?${params.toString()}`);
    },
    
    async obterConteudoAdulto(limit = 200, offset = 0) {
        return apiCall(`${this.MANGADEX_URL}/adulto?limit=${limit}&offset=${offset}`);
    },
    
    // Métodos para anúncios
    async obterAnuncios(posicao) {
        return apiCall(`${this.BASE_URL}/anuncios/${posicao}`);
    },
    
    async criarAnuncio(dados) {
        return apiCall(`${this.BASE_URL}/admin/anuncios`, {
            method: 'POST',
            body: JSON.stringify(dados)
        });
    },
    
    async atualizarAnuncio(anuncioId, dados) {
        return apiCall(`${this.BASE_URL}/admin/anuncios/${anuncioId}`, {
            method: 'PUT',
            body: JSON.stringify(dados)
        });
    },
    
    async deletarAnuncio(anuncioId) {
        return apiCall(`${this.BASE_URL}/admin/anuncios/${anuncioId}`, {
            method: 'DELETE'
        });
    },
    
    // Métodos para favoritos
    async adicionarFavorito(mangaId) {
        return apiCall(`${this.BASE_URL}/favoritos`, {
            method: 'POST',
            body: JSON.stringify({ manga_id: mangaId })
        });
    },
    
    async removerFavorito(mangaId) {
        return apiCall(`${this.BASE_URL}/favoritos/${mangaId}`, {
            method: 'DELETE'
        });
    },
    
    async obterFavoritos() {
        return apiCall(`${this.BASE_URL}/favoritos`);
    },
    
    // Métodos para histórico
    async obterHistorico() {
        return apiCall(`${this.BASE_URL}/historico`);
    },
    
    async adicionarAoHistorico(mangaId, capituloId, pagina = 0) {
        return apiCall(`${this.BASE_URL}/historico`, {
            method: 'POST',
            body: JSON.stringify({
                manga_id: mangaId,
                chapter_id: capituloId,
                last_page: pagina
            })
        });
    }
};

// Função auxiliar para buscar mangá
async function buscarManga() {
    const input = document.getElementById('search-input');
    const query = input.value.trim();
    
    if (!query) {
        showNotification('Digite um título para buscar', 'warning');
        return;
    }
    
    try {
        window.location.href = `/buscar?q=${encodeURIComponent(query)}`;
    } catch (error) {
        console.error('Erro ao buscar:', error);
        showNotification('Erro ao buscar mangá', 'error');
    }
}

// Permitir busca ao pressionar Enter
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                buscarManga();
            }
        });
    }
});
