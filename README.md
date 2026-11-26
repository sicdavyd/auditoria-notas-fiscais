## Estrutura do Projeto

A arquitetura foi organizada para isolar as camadas de persistência, integração e aplicação, permitindo que cada integrante atue em módulos distintos sem conflitos de versionamento:

```text
auditoria-notas-fiscais/
├── README.md                        # Documentação geral, instalação e divisão de tarefas
├── requirements.txt                 # Dependências do projeto (SQLAlchemy, Elasticsearch-DSL, FastAPI, RapidFuzz, Pytest)
├── .gitignore                       # Arquivos e diretórios ignorados pelo Git
├── database/                        # Camada de armazenamento local e carga inicial
│   ├── db_relacional                # Banco de dados SQLite populado com dados brutos
│   └── scripts/                     # Scripts auxiliares de saneamento, carga e validação
│       ├── limpar_json.py           # Remove entidades duplicadas da base JSON original
│       ├── popular_banco.py         # Cria as tabelas e popula o db_relacional com ruído controlado
│       └── verificar_duplicatas.py  # Consulta SQL para validar variações cadastrais no banco
├── diagrams/                        # Modelagem conceitual e física (arquivos .puml e .png)
├── infra/                           # Infraestrutura conteinerizada
│   └── docker-compose.yml           # Configuração para subir o servidor Elasticsearch
├── src/                             # Código-fonte principal da aplicação
│   ├── __init__.py
│   ├── persistencia/                # Camadas de acesso a dados (Relacional e Documental)
│   │   ├── __init__.py
│   │   ├── models.py                # Configuração do engine SQLite e entidades ORM (SQLAlchemy)
│   │   ├── orm.py                   # Operações CRUD na camada relacional
│   │   └── odm.py                   # Mapeamento Document/InnerDoc e operações CRUD no Elasticsearch
│   ├── integracao/                  # Middleware de sincronização e saneamento
│   │   ├── __init__.py
│   │   └── integrador.py            # Lê dados brutos do SQLite, normaliza e indexa no Elasticsearch
│   └── aplicacao/                   # Interfaces de interação e consulta
│       ├── __init__.py
│       ├── desktop_mvc.py           # Interface Desktop (MVC) para CRUD no banco relacional
│       ├── api_rest.py              # Backend REST (JSON) para CRUD no Elasticsearch
│       └── busca_auditoria.py       # Interface de busca por similaridade (RapidFuzz) e exportação
└── tests/                           # Suíte de testes automatizados
    ├── __init__.py
    └── test_persistencia.py         # Testes unitários com pytest validando orm.py e odm.py
```

### Resumo das Camadas

* **`database/`**: Concentra o arquivo SQLite `db_relacional` (sem extensão, conforme especificação) e os scripts responsáveis por gerar e validar a carga inicial com inconsistências realistas.
* **`infra/`**: Contém o `docker-compose.yml` para levantar a instância do Elasticsearch utilizada pela camada NoSQL.
* **`src/persistencia/`**: Centraliza a conexão e o mapeamento das entidades (`models.py`), além dos contratos CRUD relacionais (`orm.py`) e orientados a documentos (`odm.py`).
* **`src/integracao/`**: Abriga o middleware (`integrador.py`) encarregado de ler os registros não padronizados do SQLite, aplicar regras de normalização (CPF/CNPJ, GTIN, textos) e persistir no Elasticsearch sem duplicidade.
* **`src/aplicacao/`**: Reúne os pontos de entrada voltados ao usuário e à rede: interface Desktop MVC, API REST JSON e ferramenta de busca para auditoria.
* **`tests/`**: Contém os testes automatizados que asseguram a conformidade das operações de persistência com a modelagem definida.
