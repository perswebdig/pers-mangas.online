/**
 * MangaDex PT - Utilitários JavaScript
 */

// Função para fazer requisições à API
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            let errorDetail = `API Error: ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (e) {
                // Se não for JSON, pega o texto puro
                errorDetail = await response.text();
            }
            throw new Error(errorDetail);
        }
        
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('Erro na requisição:', error);
        throw error;
    }
}

// Função para mostrar notificações
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

// Função para formatar data
function formatarData(data) {
    const date = new Date(data);
    return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Função para truncar texto
function truncarTexto(texto, comprimento = 100) {
    if (texto.length <= comprimento) return texto;
    return texto.substring(0, comprimento) + '...';
}

// Função para debounce
function debounce(func, espera = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, espera);
    };
}

// Função para throttle
function throttle(func, limite = 300) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limite);
        }
    };
}

// Função para salvar no localStorage
function salvarLocal(chave, valor) {
    try {
        localStorage.setItem(chave, JSON.stringify(valor));
    } catch (error) {
        console.error('Erro ao salvar no localStorage:', error);
    }
}

// Função para obter do localStorage
function obterLocal(chave, padrao = null) {
    try {
        const item = localStorage.getItem(chave);
        return item ? JSON.parse(item) : padrao;
    } catch (error) {
        console.error('Erro ao obter do localStorage:', error);
        return padrao;
    }
}

// Função para remover do localStorage
function removerLocal(chave) {
    try {
        localStorage.removeItem(chave);
    } catch (error) {
        console.error('Erro ao remover do localStorage:', error);
    }
}

// Função para rastrear evento (analytics)
function rastrearEvento(categoria, acao, rotulo = '') {
    if (window.gtag) {
        gtag('event', acao, {
            'event_category': categoria,
            'event_label': rotulo
        });
    }
}

// Função para detectar dispositivo
function ehMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

// Função para verificar conexão
async function verificarConexao() {
    try {
        const response = await fetch('/health');
        return response.ok;
    } catch {
        return false;
    }
}

// Função para scroll suave
function scrollSuave(elemento) {
    elemento.scrollIntoView({ behavior: 'smooth' });
}

// Função para copiar para clipboard
async function copiarParaClipboard(texto) {
    try {
        await navigator.clipboard.writeText(texto);
        showNotification('Copiado para clipboard!', 'success');
    } catch (error) {
        console.error('Erro ao copiar:', error);
        showNotification('Erro ao copiar', 'error');
    }
}

// Função para gerar ID único
function gerarID() {
    return '_' + Math.random().toString(36).substr(2, 9);
}

// Função para validar email
function validarEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

// Função para validar URL
function validarURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Verificar conexão ao iniciar
    verificarConexao().then(conectado => {
        if (!conectado) {
            showNotification('Sem conexão com o servidor', 'error');
        }
    });
    
    // Adicionar listener para mudanças de conexão
    window.addEventListener('online', () => {
        showNotification('Conexão restaurada', 'success');
    });
    
    window.addEventListener('offline', () => {
        showNotification('Sem conexão', 'error');
    });
});
