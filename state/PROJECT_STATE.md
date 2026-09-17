# Estado do projeto

**Atualizado em:** 2026-09-17

## Onde estamos

Roadmap item 1 (Variáveis + Benefícios → Questor, cliente ART LATEX) em
andamento. **147/147 testes passando** (excluindo os dois arquivos com
dependências ausentes no ambiente).

Extração real implementada e validada para 5 eventos, sobre a camada
canônica já construída, **sem liberar produção** e **sem tocar no
bloqueio do tipo H**:

- `src/jrdp/minutos.py` — proteção permanente: H,MM nunca é somado como
  decimal (01:52+00:32 = 144 minutos/02:24, nunca "1,84").
- `src/jrdp/extratores/` — `valor_simples.py` (Vale-refeição,
  Vale-compras, Convênio Farmácia, Adicional Noturno), `cesta_basica.py`,
  `horas.py` (Hora-extra, estrutural, sem dados reais para validar),
  `vale_transporte.py` (propositalmente PENDENTE — zero registros reais).

**Validação real agregada** (nenhum dado individual persistido): VR
Filial 233/190/43, Compras Filial 21/16/5, Farmácia Filial 7/5/2,
Adicional Noturno Filial 44/33/11, Cesta Matriz+Filial 317/304/13
(total/encontrados/não encontrados). Todos `BLOCKED` pela política
fail-closed — esperado, confirma que o gate funciona.

**Conflito resolvido a favor da evidência física**: uma instrução pedia
"Matriz: coluna E Desconto" para a Cesta Básica — isso contradiz achado
já registrado (coluna real é `CR`, sem coluna de valor). Não foi seguido;
a regra confirmada (contagem × R$1,00) foi mantida.

**Achado novo (PENDENTE)**: a Matriz tem dados reais de Vale-refeição,
Vale-compras, Convênio Farmácia e Adicional Noturno, mas nenhum código de
evento confirmado para essas abas nessa unidade — não foi assumido que os
códigos da Filial se aplicam.

Continuam PENDENTES: certificação binária tipo H, versão do Questor,
Vale-transporte (zero dados reais + coluna de valor não confirmada).

Detalhes completos em `docs/P01_ART_LATEX_QUESTOR.md` e
`docs/DECISIONS.md` (entradas de 2026-09-17). Nenhum dado pessoal foi
reproduzido em qualquer lugar versionado. Nenhum exportador ligado à
produção — `BLOCKED` global do P01 continua valendo.

## Próximo passo

Três decisões dependem do usuário:
1. Códigos de evento da Matriz para Vale-refeição/Vale-compras/Convênio
   Farmácia/Adicional Noturno (mesmos da Filial? diferentes? não existem?).
2. Fluxo operacional para corrigir nomes não encontrados (ex.: os 43 da
   VR Filial) — quem corrige, onde, e como re-rodar depois.
3. Arquivo `.csv` real tipo H e/ou versão do Questor, quando disponíveis.

## Como retomar

Rodar `/retomar-projeto` no início da sessão.
