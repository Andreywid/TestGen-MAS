# TestGen-MAS

Sistema multi-agente para geracao automatica de testes unitarios em Python usando LLMs.

Voce passa uma funcao Python e o sistema gera testes `pytest` para ela: analisa o codigo, propoe casos de teste via LLM, executa os testes e corrige falhas automaticamente.

## Como funciona

O sistema tem dois modos de operacao.

**Single-agent:** um unico agente LLM recebe o codigo-fonte e gera o arquivo de testes completo, incluindo os valores esperados. Rapido e direto, sem analise previa.

**Multi-agent:** pipeline com seis agentes especializados:

```
codigo-fonte
    |
    Analyzer   analisa o codigo e produz briefing (casos normais, edge cases, branches)
    |
    Generator  gera o arquivo pytest a partir do codigo e do briefing
    |
    Executor   roda pytest com cobertura e coleta resultados
    |
    Reviewer   diagnostica cada teste que falhou
    |
    Refiner    reescreve os testes com problema, um por vez
    |
    Validator  aprova apenas os testes que passaram e tem cobertura
```

O loop Reviewer-Refiner repete ate 3 vezes ou ate nao restar falhas. O pipeline e monotono: se uma iteracao de refinamento regredir, o arquivo anterior e restaurado automaticamente.

**Modelos:** por padrao, Analyzer e Reviewer usam `llama-3.3-70b-versatile` e Generator e Refiner usam `llama-3.1-8b-instant`. O modelo e configuravel via argumento na linha de comando (ver secao Como rodar).

## Resultados

Benchmark nas 15 funcoes do [HumanEval](https://github.com/openai/human-eval). Fatorial 2x2: dois modos de operacao cruzados com dois modelos.

### Resumo

| Modo | Pass-rate | Testes | Chamadas LLM | Tempo | Refinamentos |
|------|:---:|:---:|:---:|:---:|:---:|
| Single (8b) | 13/15 | 89 | 14 | ~24s | n/a |
| Multi (8b) | 13/15 | 106 | 90 | ~657s | 0/15 |
| Single (70b) | 15/15 | 152 | 15 | ~26s | n/a |
| Multi (70b) | 15/15 | 170 | 110 | ~358s | 10/15 |

### Resultados por funcao

| Funcao | Single (8b) | Multi (8b) | Single (70b) | Multi (70b) |
|--------|:---:|:---:|:---:|:---:|
| `has_close_elements` | 7t / 100% | 15t / 100% | 9t / 100% | 16t / 100% |
| `separate_paren_groups` | 0t / 0% | 3t / 100% | 12t / 100% | 12t / 100% |
| `truncate_number` | 5t / 100% | 3t / 100% | 9t / 100% | 8t / 100% |
| `below_zero` | 8t / 100% | 16t / 100% | 13t / 100% | 11t / 100% |
| `mean_absolute_deviation` | TIMEOUT | 3t / 100% | 8t / 100% | 11t / 100% |
| `fizz_buzz` | 4t / 100% | TIMEOUT | 10t / 100% | 11t / 100% |
| `will_it_fly` | 10t / 100% | 12t / 100% | 11t / 100% | 13t / 100% |
| `is_happy` | 7t / 100% | 15t / 100% | 10t / 100% | 6t / 100% |
| `any_int` | 8t / 100% | 10t / 100% | 5t / 100% | 12t / 83% |
| `reverse_delete` | 8t / 100% | 4t / 100% | 16t / 100% | 17t / 100% |
| `match_parens` | 9t / 100% | 0t / 0% | 12t / 100% | 5t / 100% |
| `valid_date` | 4t / 88% | 5t / 88% | 7t / 100% | 13t / 100% |
| `is_sorted` | 8t / 100% | 11t / 100% | 11t / 100% | 10t / 100% |
| `intersection` | 4t / 88% | 8t / 94% | 9t / 75% | 13t / 94% |
| `fix_spaces` | 7t / 95% | 1t / 95% | 10t / 100% | 12t / 100% |
| **Total** | **89t, 13/15** | **106t, 13/15** | **152t, 15/15** | **170t, 15/15** |
| **Custo** | **14 c / 24s** | **90 c / 657s** | **15 c / 26s** | **110 c / 358s** |

### Conclusoes

**Modelo determina o pass-rate; arquitetura determina a qualidade dos testes.** Com 8b, ambos os modos ficam em 13/15 independente da arquitetura. Com 70b, ambos chegam a 15/15. A diferenca entre single e multi com 70b e 18 testes a mais e refinamento efetivo em 10 de 15 funcoes.

**O loop Reviewer-Refiner so funciona com o Refiner no modelo forte.** Com 8b no Refiner, `refinement_iterations = 0` em todos os casos. Com 70b, 10 de 15 funcoes foram melhoradas: `fizz_buzz` e `match_parens` precisaram de 3 iteracoes cada para convergir, exatamente as funcoes que causavam timeout ou 0 testes nos modos com 8b.

**Single-70b e o melhor custo/beneficio.** Atinge 15/15 com 15 chamadas em 26 segundos, o mesmo custo do single-8b. Multi-70b tambem chega a 15/15, mas usa 7x mais chamadas e leva 14x mais tempo. Para suites mais ricas em edge cases, multi-70b gera testes mais sistematicos.

**Falhas do modelo 8b sao estocasticas.** A mesma funcao pode gerar 0 testes em um run e 4 no seguinte. O modelo 70b elimina essa variancia: nenhuma funcao deu timeout ou 0 testes em nenhuma das duas configuracoes.

**Proxima etapa: mutation testing.** Pass-rate e cobertura nao separam single-70b de multi-70b. Para medir qual suite detecta mais bugs reais, o passo seguinte e rodar mutantes com `mutmut` ou `cosmic-ray`.

## Stack

- LLM: Groq API (`llama-3.3-70b-versatile` e `llama-3.1-8b-instant`)
- Testes: pytest + pytest-cov
- Orquestracao: Python puro, sem LangChain nem CrewAI
- Dataset: [HumanEval](https://github.com/openai/human-eval) (MIT)

## Pre-requisitos

- Python 3.10 ou superior
- Chave de API do Groq, gratuita em [console.groq.com](https://console.groq.com)

## Instalacao

```bash
git clone <url-do-repositorio>
cd testgen-mas

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie o arquivo de configuracao:

```bash
cp .env.example .env
```

Edite `.env` e insira sua chave:

```
GROQ_API_KEY=gsk_...
```

## Como rodar

```bash
# Ambos os modos com configuracao padrao (Analyzer/Reviewer=70b, Generator/Refiner=8b)
python main.py

# Somente um modo
python main.py single_agent
python main.py multi_agent

# Fixar o modelo para todos os agentes
python main.py 8b
python main.py 70b

# Combinar modo e modelo
python main.py single_agent 70b
python main.py multi_agent 8b
```

A saida mostra o progresso em tempo real e uma tabela comparativa ao final.

Os resultados sao salvos em `results/` como JSON. Quando dois modos rodam juntos, um arquivo `summary_*.json` agrega tudo.

## Estrutura

```
testgen-mas/
├── agents/
│   ├── analyzer.py      analisa o codigo e produz briefing estruturado
│   ├── generator.py     gera arquivo pytest a partir do codigo e do briefing
│   ├── executor.py      executa pytest com cobertura e parseia a saida
│   ├── reviewer.py      diagnostica falhas por teste
│   ├── refiner.py       reescreve testes com problema
│   └── validator.py     filtro final sem LLM
├── core/
│   ├── models.py        estruturas de dados compartilhadas
│   ├── llm_client.py    cliente da Groq API com retry
│   └── pipeline.py      orquestrador dos dois modos
├── data/
│   └── humaneval_samples/
│       └── samples.py   15 funcoes HumanEval
├── results/             JSONs de saida por execucao (ignorado pelo git)
├── main.py              ponto de entrada com saida visual no terminal
├── requirements.txt
└── .env.example
```

## Licenca

MIT. Dataset HumanEval: MIT, [openai/human-eval](https://github.com/openai/human-eval).
