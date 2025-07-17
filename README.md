# Adversarial Search Strategies and Decision Trees

## Descrição
Este projeto implementa e compara diferentes estratégias de pesquisa adversarial para o jogo Connect Four, utilizando **Monte Carlo Tree Search (MCTS)** e **árvores de decisão**. O foco é analisar o desempenho de quatro variantes do MCTS e aplicar o algoritmo **ID3** tanto ao dataset Iris como a dados gerados pelos MCTS.

Projeto desenvolvido na **Faculdade de Ciências da Universidade do Porto (FCUP)** no âmbito da disciplina de **Inteligência Artificial**.

---

## Funcionalidades

- Implementação de quatro variantes do MCTS:
  - **MCTS1**: Implementação canónica.
  - **MCTS2**: Com estratégia progressive widening.
  - **MCTS3**: Com heurísticas táticas para jogadas críticas.
  - **MCTSID3**: Integração com árvore de decisão ID3.
- Algoritmo **ID3** aplicado a:
  - Dataset Iris com discretização de atributos.
  - Dataset Connect Four gerado automaticamente.
- Interface gráfica interativa para:
  - Jogos Human vs AI.
  - Confrontos AI vs AI.
  - Sistema de sugestões de jogadas.
- Análise de performance:
  - 100 partidas controladas por configuração.
  - Métricas de classificação (accuracy, precision, recall, F1-score).
  - Visualização de resultados.

---

## Tecnologias Utilizadas

- **Python 3.10.12**
- Bibliotecas:
 - `pygame 2.6.1`
 - `numpy 2.2.3`
 - `scikit-learn 1.6.1`
 - `matplotlib 3.10.0`
 - `pandas 2.2.3`
 - `joblib 1.4.2`
