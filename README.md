# MangaDex PT - FastAPI + PostgreSQL

Plataforma web elegante e responsiva para leitura de mangás com integração completa à API MangaDex, desenvolvida em **FastAPI** com **HTML/CSS/JavaScript puro**.

## 🚀 Características

- ✅ Integração completa com API MangaDex
- ✅ Interface responsiva (mobile, tablet, desktop)
- ✅ Categorias com filtros avançados
- ✅ Sistema de busca por título
- ✅ Página de detalhes com lista de capítulos
- ✅ Módulo de conteúdo adulto (hentai)
- ✅ Sistema de anúncios (header, footer, leitor, popunder, social bar)
- ✅ Painel de administração
- ✅ 100% em português brasileiro
- ✅ Leve e rápido (sem dependências pesadas)

## 📋 Requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🔧 Instalação

### 1. Clonar ou Baixar o Projeto

```bash
cd mangadex-pt-fastapi
```

### 2. Criar Ambiente Virtual

```bash
python -m venv venv

# No Windows
venv\Scripts\activate

# No Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
DATABASE_URL=postgresql://mangadex_user:senha_segura@localhost:5432/mangadex_db
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
DEBUG=False
PORT=8000
```

### 5. Criar Banco de Dados

```bash
# Criar banco de dados PostgreSQL
createdb -U postgres mangadex_db

# Ou via psql
psql -U postgres
CREATE DATABASE mangadex_db;
```

### 6. Executar Aplicação

```bash
python main.py
```

A aplicação estará disponível em: `http://localhost:8000`

## 📁 Estrutura do Projeto

```
mangadex-pt-fastapi/
├── main.py                 # Aplicação FastAPI principal
├── models.py              # Modelos SQLAlchemy
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de variáveis de ambiente
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── categorias.html
│   ├── buscar.html
│   ├── manga_detalhes.html
│   ├── adulto.html
│   ├── components/
│   │   ├── header.html
│   │   └── footer.html
│   └── admin/
│       ├── dashboard.html
│       └── anuncios.html
├── static/               # Arquivos estáticos
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── utils.js
│   │   ├── api.js
│   │   └── ads.js
│   └── images/
└── migrations/           # Migrations do banco de dados
```

## 🌐 Endpoints da API

### Mangás

- `GET /` - Página inicial
- `GET /api/mangadex/populares` - Mangás populares
- `GET /api/mangadex/buscar?q=query` - Buscar mangás
- `GET /api/mangadex/manga/{id}` - Detalhes do mangá
- `GET /api/mangadex/manga/{id}/capítulos` - Capítulos do mangá
- `GET /api/mangadex/categorias` - Categorias disponíveis
- `GET /api/mangadex/filtrar` - Filtrar mangás
- `GET /api/mangadex/adulto` - Conteúdo adulto

### Anúncios

- `GET /api/anuncios/{posicao}` - Obter anúncios
- `POST /api/admin/anuncios` - Criar anúncio
- `PUT /api/admin/anuncios/{id}` - Atualizar anúncio
- `DELETE /api/admin/anuncios/{id}` - Deletar anúncio

### Health

- `GET /health` - Verificar saúde da aplicação

## 🎨 Customização

### Cores

Edite as variáveis CSS em `static/css/style.css`:

```css
:root {
    --primary: #6366f1;
    --secondary: #ec4899;
    --accent: #8b5cf6;
    /* ... */
}
```

### Tipografia

Adicione fontes customizadas em `templates/base.html`:

```html
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
```

## 📱 Responsividade

A aplicação é totalmente responsiva com breakpoints para:

- Mobile: até 767px
- Tablet: 768px a 1023px
- Desktop: 1024px+
- Large: 1440px+

## 🔐 Segurança

- Use variáveis de ambiente para dados sensíveis
- Configure HTTPS em produção
- Valide todas as entradas do usuário
- Use CORS appropriadamente

## 📊 Performance

- CSS e JS minificados
- Lazy loading de imagens
- Cache de dados da API
- Compressão gzip

## 🐛 Troubleshooting

### Erro: "Database connection failed"

Verifique se PostgreSQL está rodando e as credenciais estão corretas no `.env`.

### Erro: "Module not found"

Certifique-se de que o ambiente virtual está ativado e as dependências foram instaladas:

```bash
pip install -r requirements.txt
```

### Erro: "Port already in use"

Mude a porta no `.env`:

```env
PORT=8001
```

## 📝 Licença

MIT License - Veja LICENSE para mais detalhes

## 🤝 Contribuições

Contribuições são bem-vindas! Abra uma issue ou pull request.

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato.

---

**Versão**: 1.0.0  
**Data**: 30/01/2026  
**Desenvolvido com ❤️ em Python**
