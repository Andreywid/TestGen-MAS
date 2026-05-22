# TestGen-MAS
### A Multi-Agent LLM-Based System for Automated Unit Test Generation and Refinement

Projeto prático de Engenharia de Software & Inteligência Artificial focado em automação de testes utilizando arquiteturas multi-agentes baseadas em LLMs.

---

## Sobre o Projeto

O **TestGen-MAS** investiga o uso de múltiplos agentes especializados para geração, execução, revisão e refinamento automático de testes unitários em Python.

A proposta compara uma abordagem tradicional **Single-Agent** com uma arquitetura **Multi-Agent**, avaliando qualidade, cobertura e executabilidade dos testes gerados.

O projeto atua na fase de **Testes e Garantia de Qualidade** do ciclo de vida de software (SDLC).

---

# Objetivo

Desenvolver e avaliar um sistema multi-agente baseado em LLMs capaz de:

- Gerar testes unitários automaticamente
- Executar os testes utilizando `pytest`
- Detectar falhas e problemas
- Refinar os testes iterativamente
- Melhorar cobertura e qualidade dos testes

---

# Arquitetura Multi-Agente

O sistema é composto por quatro agentes especializados.

---

## 1. Test Generator Agent

Responsável por gerar testes unitários automaticamente a partir de funções Python.

### Entrada
- Código-fonte da função

### Saída
- Arquivo de testes em `pytest`

---

## 2. Test Executor Agent

Executa os testes gerados e coleta métricas.

### Responsabilidades
- Rodar `pytest`
- Capturar erros
- Medir cobertura de código
- Registrar logs de execução

---

## 3. Test Reviewer Agent

Analisa os resultados obtidos após a execução.

### Responsabilidades
- Identificar falhas
- Detectar asserts incorretos
- Detectar imports inexistentes
- Encontrar testes superficiais

---

## 4. Test Refiner Agent

Refina e corrige os testes automaticamente com base no feedback do Reviewer.

### Responsabilidades
- Corrigir asserts
- Ajustar imports
- Melhorar cobertura
- Regenerar testes problemáticos

---

# Fluxo de Execução

```text
Código Python
      ↓
Test Generator Agent
      ↓
Test Executor Agent
      ↓
Test Reviewer Agent
      ↓
Test Refiner Agent
      ↓
Testes Refinados
```

---

# Experimento

O experimento compara duas abordagens:

## Condição 1 — Single-Agent

Um único agente gera os testes diretamente, sem refinamento posterior.

## Condição 2 — Multi-Agent

Os quatro agentes executam o pipeline completo com refinamento iterativo.