/**
 * MangaDex PT - Gerenciador de Anúncios
 */

const AdsManager = {
    // Configurações
    config: {
        header: { posicao: 'header', altura: '100px' },
        footer: { posicao: 'footer', altura: '100px' },
        reader: { posicao: 'reader', altura: '300px' },
        popunder: { posicao: 'popunder', altura: '600px' },
        social: { posicao: 'social', altura: 'auto' }
    },
    
    // Carregador de anúncios
    async carregarAnuncios(posicao) {
        try {
            const dados = await API.obterAnuncios(posicao);
            if (dados.anuncios && dados.anuncios.length > 0) {
                this.renderizarAnuncio(posicao, dados.anuncios[0]);
            }
        } catch (error) {
            console.error(`Erro ao carregar anúncios de ${posicao}:`, error);
        }
    },
    
    // Renderizar anúncio
    renderizarAnuncio(posicao, anuncio) {
        const container = document.getElementById(`${posicao}-ad`);
        if (!container) return;
        
        const elemento = document.createElement('div');
        elemento.className = 'ad-container';
        elemento.innerHTML = `
            <a href="${anuncio.click_url}" target="_blank" rel="noopener noreferrer" class="ad-link">
                <img src="${anuncio.image_url}" alt="${anuncio.title}" class="ad-image">
                <div class="ad-info">
                    <h4>${anuncio.title}</h4>
                    <p>${anuncio.description}</p>
                </div>
            </a>
        `;
        
        // Rastrear impressão
        this.rastrearImpressao(anuncio.id);
        
        // Rastrear clique
        elemento.querySelector('.ad-link').addEventListener('click', () => {
            this.rastrearClique(anuncio.id);
        });
        
        container.innerHTML = '';
        container.appendChild(elemento);
    },
    
    // Rastrear impressão
    rastrearImpressao(anuncioId) {
        // Enviar evento de impressão ao servidor
        apiCall(`/api/ads/${anuncioId}/impression`, {
            method: 'POST'
        }).catch(error => console.error('Erro ao rastrear impressão:', error));
    },
    
    // Rastrear clique
    rastrearClique(anuncioId) {
        // Enviar evento de clique ao servidor
        apiCall(`/api/ads/${anuncioId}/click`, {
            method: 'POST'
        }).catch(error => console.error('Erro ao rastrear clique:', error));
    },
    
    // Carregar todos os anúncios
    async carregarTodos() {
        for (const posicao of Object.keys(this.config)) {
            await this.carregarAnuncios(posicao);
        }
    },
    
    // Mostrar popunder
    mostrarPopunder() {
        const anuncio = document.getElementById('popunder-ad');
        if (anuncio && anuncio.querySelector('.ad-container')) {
            // Abrir em nova aba após delay
            setTimeout(() => {
                window.open('', '_blank');
            }, 3000);
        }
    },
    
    // Inicializar social bar
    inicializarSocialBar() {
        const socialBar = document.getElementById('social-bar');
        if (!socialBar) return;
        
        const redes = [
            { nome: 'Twitter', url: 'https://twitter.com', icon: '𝕏' },
            { nome: 'Discord', url: 'https://discord.com', icon: '💬' },
            { nome: 'GitHub', url: 'https://github.com', icon: '🐙' }
        ];
        
        redes.forEach(rede => {
            const item = document.createElement('a');
            item.href = rede.url;
            item.target = '_blank';
            item.rel = 'noopener noreferrer';
            item.className = 'social-bar-item';
            item.title = rede.nome;
            item.textContent = rede.icon;
            socialBar.appendChild(item);
        });
    }
};

// Inicializar ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Carregar anúncios
    AdsManager.carregarTodos();
    
    // Inicializar social bar
    AdsManager.inicializarSocialBar();
    
    // Mostrar popunder após alguns segundos
    setTimeout(() => {
        AdsManager.mostrarPopunder();
    }, 5000);
});

// Recarregar anúncios periodicamente (a cada 5 minutos)
setInterval(() => {
    AdsManager.carregarTodos();
}, 5 * 60 * 1000);
