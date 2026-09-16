# Testing

Aplica-se a qualquer mudança em `src/jrdp/`.

## Regra

- Nenhuma automação é considerada pronta sem testes cobrindo:
  - caminho feliz;
  - entradas inválidas/limites;
  - regras de negócio explicitamente confirmadas (ex.: formato H,MM);
  - regressões de bugs já corrigidos (ex.: garantir que 01:30 nunca vira
    1,50 em vez de 1,30).
- Rodar `pytest` antes de qualquer commit que toque `src/` ou `tests/`.
- Um teste que trava uma regra de negócio sensível (ex.: serialização de
  hora) deve ter nome explícito citando a regra, não apenas "test_format".
