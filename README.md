
# 🟠 BTC Dashboard – Streamlit

Monitor de mercado em tempo real usando **Binance** / **CoinGecko** + **Crypto Fear & Greed Index (Alternative.me)**  
Inclui:

- Preços do BTC/USDT  
- Variação 24h  
- Volume  
- Índice de sentimento (FNG)  
- Gráficos interativos  
- Overlay *Preço × Sentimento*  
- Cards coloridos dinâmicos  
- Cache inteligente  
- Arquitetura modular por componentes  

---

## 📸 Screenshots

> *(Adicione aqui imagens do seu aplicativo rodando)*  
> Exemplo:  
> - `screenshots/dashboard.png`  
> - `screenshots/overlay.png`

---

## 🚀 Tecnologias

- **Python 3.10+**
- **Streamlit**
- **Pandas**
- **Altair**
- **Requests**
- **Binance/CoinGecko REST API**
- **Alternative.me Fear & Greed API**

---

## 📁 Estrutura do Projeto

```
app/
│
├── api/
│   └── alternative_me.py       # Fear & Greed Index
│   ├── binance.py              # Preços + klines
│   ├── coin_gecko.py           # Preços + klines
│
├── components/
│   ├── metrics.py              # Cards coloridos + CSS
│   └── tabs.py                 # Abas (Preço, Sentimento, Debug)
│
├── utils/
│   └── formaters.py            # Funções auxiliares
│
└── dashboard.py                # Ponto principal da aplicação Streamlit
```

---

## 🔌 APIs Utilizadas

### 📈 **Binance API**

**Ticker 24h**  
`GET https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT`

**Klines (Preço diário)**  
`GET https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1d&limit=365`

---

### 📈 **CoinGecko API**

**Ticker 24h**  
`GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_24hr_high_low=true`

**Klines (Preço diário)**  
`GET https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=365&interval=daily`

---

### 🧠 **Alternative.me – Fear & Greed Index**
`GET https://api.alternative.me/fng/?limit=N&format=json`

---

## 🧱 Instalação

### Clone o projeto:

```bash
git clone https://github.com/seuusuario/btc-dashboard.git
cd btc-dashboard
```

### Crie um ambiente virtual e ative-o:

```bash
python -m venv venv
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows
```

### Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução

```bash
streamlit run app/dashboard.py
```

A aplicação abrirá automaticamente no navegador:

```
http://localhost:8501
```

---

## 🧩 Componentes

### 🔶 1. **Cards de Métricas (`components/metrics.py`)**
- Cores dinâmicas (verde, vermelho, roxo, amarelo, neutro)
- CSS customizado injetado automaticamente
- Ideal para dashboards de cripto

### 🔶 2. **Abas (`components/tabs.py`)**
Inclui:
- Gráfico de preços (line chart)
- Tabela rolável
- Gráfico do Fear & Greed
- Tabela de sentimento
- Overlay: **Preço × FNG** com dois eixos Y

### 🔶 3. **APIs (`api/`)**
- `binance.py` — dados de preço, volume, klines  
- `alternative_me.py` — Fear & Greed Index

---

## 🎨 Funcionalidades de UI

✔ Layout responsivo  
✔ Cards coloridos dinâmicos  
✔ Abas separadas para cada tipo de dado  
✔ Tabelas com rolagem  
✔ Overlay Altair altamente visual  
✔ Auto-refresh opcional  
✔ Cache inteligente (Streamlit `cache_data`)  

---

## 📊 Overlay Preço × Fear & Greed

O gráfico overlay combina:

- preço do BTC (linha azul)
- índice de sentimento (linha laranja tracejada)
- ambos com eixos independentes

Ideal para identificar:

- Divergências  
- Euforia extrema  
- Capitulação  
- Possíveis pontos de reversão    

---

## 📄 Licença

MIT — totalmente livre para modificar ou distribuir.

---

## 🙋‍♂️ Autor

**Marcio Martinez (@masioware)**  
