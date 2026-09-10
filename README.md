# Weather Data Pipeline

Pipeline em Python que coleta dados de clima em tempo real para cidades dos EUA via [OpenWeatherMap](https://openweathermap.org/api) e carrega os dados brutos (JSON) em uma tabela no Snowflake para análise posterior.

## Arquitetura

```
city.list.json (lista global de cidades da OpenWeatherMap)
        │
        ▼
extract_cities.py  ──►  city_final_list.json (apenas cidades dos EUA: nome + coordenadas)
        │
        ▼
weather_api_pipeline.py
        │  para cada cidade:
        │    1. chama a API do OpenWeatherMap
        │    2. insere o JSON bruto na tabela RAW.raw_weather (Snowflake)
        ▼
   Snowflake (WEATHER_DB.RAW.raw_weather)
```

`find_country.py` é um script auxiliar usado durante a exploração inicial do dataset (não faz parte do fluxo principal).

Um exemplo da resposta da API está em [`sample_output/weather_data_sample.json`](sample_output/weather_data_sample.json).

## Stack

- Python 3
- [requests](https://pypi.org/project/requests/) — chamadas à API do OpenWeatherMap
- [snowflake-connector-python](https://pypi.org/project/snowflake-connector-python/) — carga no Snowflake
- [python-dotenv](https://pypi.org/project/python-dotenv/) — variáveis de ambiente

## Estrutura do projeto

```
weather-pipeline/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── sample_output/
│   └── weather_data_sample.json
└── src/
    ├── extract_cities.py
    ├── find_country.py
    └── weather_api_pipeline.py
```

## Setup

1. Clone o repositório e crie um ambiente virtual:

   ```bash
   git clone https://github.com/<seu-usuario>/weather-pipeline.git
   cd weather-pipeline
   python -m venv venv
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

2. Copie `.env.example` para `.env` e preencha com suas credenciais (nunca commite o `.env`):

   ```bash
   copy .env.example .env      # Windows
   ```

   | Variável | Descrição |
   |---|---|
   | `API_KEY` | Chave da API do OpenWeatherMap |
   | `SNOWFLAKE_USER` | Usuário do Snowflake |
   | `SNOWFLAKE_PASSWORD` | Senha do Snowflake |
   | `SNOWFLAKE_ACCOUNT` | Identificador da conta Snowflake |
   | `SNOWFLAKE_WAREHOUSE` | Warehouse a ser usado |
   | `SNOWFLAKE_DATABASE` | Database de destino |
   | `SNOWFLAKE_SCHEMA` | Schema de destino |
   | `SNOWFLAKE_ROLE` | Role usada na conexão |

3. Baixe o dataset completo de cidades ([`city.list.json`](https://openweathermap.org/current#cityid) da OpenWeatherMap) e coloque na raiz do projeto.

4. Crie a tabela de destino no Snowflake:

   ```sql
   CREATE TABLE IF NOT EXISTS raw_weather (
       raw_data VARIANT
   );
   ```

## Como rodar

```bash
python src/extract_cities.py       # gera city_final_list.json
python src/weather_api_pipeline.py # coleta o clima e carrega no Snowflake
```

## Melhorias futuras

- Testes automatizados para as funções de extração e transformação
- Agendamento via cron / GitHub Actions / Airflow para execução periódica
- Camada de transformação (ex.: dbt) sobre os dados brutos no Snowflake
- Retry com backoff exponencial nas chamadas à API
