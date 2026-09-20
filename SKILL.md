---
name: estimativa-conversao-flex
description: >
  Mensura as horas de conversão de telas Flex (.swf) de addon/módulo Sankhya para HTML5,
  extraindo métricas direto dos binários publicados quando não há código-fonte. Aplica o
  modelo calibrado (índice = membros + 0,5×widgets + 2×serviços; 8h + 0,18×índice + 2,5h/popup),
  monta o backlog por tela e entrega o JSON pronto para a skill orcamento-horas-docx.
  Acionar para "orçamento de conversão de addon", "converter telas Flex para HTML5",
  "quantas horas para converter esse addon", "estimar migração de Flex", "orçar conversão
  de swf", "addon antigo em Flex", "tela descontinuada pelo navegador".
  Não usar para estimar desenvolvimento novo — para isso, sankhya-estimativa-planejador.
---

# Estimativa de conversão de telas Flex para HTML5

Addon Sankhya antigo tem as telas em `.swf` e, quase sempre, **sem código-fonte** no pacote
entregue. Esta skill mede o esforço a partir dos binários publicados.

Premissa central: **o backend não é reescrito.** As telas Flex conversam com beans EJB via
`ServiceProxy`; a tela HTML5 chama os mesmos serviços. Só o cliente é reconstruído. Se essa
premissa cair, o modelo aqui não serve.

## Fluxo

### 1. Reconhecer o pacote

Mapeie antes de medir:

```
<addon>/
├── extension.xml                     # id, versão, vendor, módulo licenciado
├── ejb/*.jar                         # backend — verificar se há .java ou só .class
├── web/<ctx>/flex/*.swf              # AS TELAS A CONVERTER
├── web/<ctx>/flex/launcher/*.body    # configuracaoTela
├── web/<ctx>/flex/launcher/*.i18n    # chaves de tradução (conta como esforço)
├── web/<ctx>/flex/launcher/*.parameters  # parâmetros MGE lidos pela tela
├── web/<ctx>/WEB-INF/resources/service-providers.xml  # domínios de serviço
├── web/<ctx>/html5/ ou portal/       # o que JÁ está convertido — não orçar
├── datadictionary/metadata.xml
└── dbscripts/*.sql
```

Registre e reporte:

- **Serviços expostos** (`service-providers.xml`) — são o contrato que sobrevive.
- **Quantas chaves i18n** — 200 chaves é trabalho real de migração, entra no item de estrutura.
- **Quantos parâmetros MGE** e **configurações de tela** a tela lê — cada um é um caminho
  de comportamento a reproduzir e a homologar.
- **O que já é HTML** — portal, telas html5 já convertidas. Vai para escopo negativo.
  Nunca orçar conversão do que não é Flex.
- **Se existe tela do mesmo módulo já convertida.** Se existe, é régua interna e o risco cai.
  Se não existe, dizer isso explicitamente na seção de risco.

Ignore `framework_*.swf` e `playerProductInstall.swf` — são runtime Flex, não telas.

### 2. Extrair o constant pool

Os SWF são `CWS` (zlib). O extrator descomprime, varre as tags `DoABC` (código 82) e despeja
o constant pool de strings: caminhos de fonte, classes, membros, componentes MXML,
SQL embutido e chamadas de serviço.

```bash
mkdir -p _analise-conversao-html5/scripts
cd web/<ctx>/flex
for f in *.swf; do
  python ~/.claude/skills/estimativa-conversao-flex/scripts/extrai-swf-abc.py \
    "$f" "<destino>/${f%.swf}.txt"
done
```

Descubra o nome do workspace Flex original olhando os caminhos extraídos — algo como
`D:\sk-java\workspace\3.11\Cotacao-VC-Flex\src;...`. Esse fragmento é o filtro que separa
código do cliente do framework Adobe.

### 3. Medir

```bash
python ~/.claude/skills/estimativa-conversao-flex/scripts/metricas-swf.py \
  <dir_txt> "<Nome-VC-Flex>" \
  --servicos "DominioSP,OutroDominioSP" \
  --json metricas.json
```

Saída por SWF e por classe: membros, handlers MXML, bindings, widgets, serviços, popups,
índice e horas.

**Revise o que o script chuta.** A contagem de popup é heurística (`^Popup`/`^PopUp`) e erra
em janela auxiliar com outro nome — `Preferencias`, `Configuracoes`, `Wizard*`. Some os
popups faltantes na mão, a 2,5h cada.

### 4. Ajustar antes de fechar

O número bruto do script é ponto de partida, não resposta. Aplique:

| Situação | Ajuste |
|---|---|
| Classe repetida em mais de um SWF (mesmo popup publicado 2×) | Contar uma vez; no segundo SWF, só 4h de registro/publicação |
| Tela já convertida no pacote | Zerar. Vai para escopo negativo |
| Popup não detectado pelo `^Popup` | +2,5h cada |
| Design System novo (`ez-`/`snk-`, pipeline Node) em vez de sankhya-js | Multiplicar desenvolvimento por ~1,4 e somar setup de build |
| Código-fonte Flex disponível | Reduzir o item de levantamento em ~40% |
| Integração com serviço externo (operadora, SEFAZ, balança) | Homologação sobe; sinalizar dependência de credencial |

### 5. Somar infraestrutura e fases

Telas nunca são o orçamento inteiro. Some três itens de desenvolvimento, dimensionados pelo
número de telas e pelo volume de i18n/parâmetros:

| Item | Referência |
|---|---|
| Estrutura, publicação e registro das telas | 12h (3–4 telas) a 16h (9–10 telas) |
| Levantamento do comportamento atual | 16h a 24h; **este é o item que estoura** |
| Adequação das rotinas de servidor existentes | 10h a 12h |

Depois, as demais fases como percentual do desenvolvimento total:

| Fase | % do desenvolvimento |
|---|---|
| Alinhamento / definições | ~6% |
| Homologação | ~12% |
| Documentação | ~5% |

### 6. Redigir e gerar o DOCX

Monte o JSON no schema da skill `orcamento-horas-docx` e delegue a renderização a ela.
**Não escrever DOCX à mão.**

Regras de redação, sem exceção:

- **Linguagem de negócio.** O leitor é comprador, não desenvolvedor. Nunca aparecem no
  documento: Flex, SWF, MXML, EJB, AngularJS, bean, popup, binding, DynamicForm, widget.
  Diga "tecnologia descontinuada pelos navegadores", "rotinas de servidor", "janela auxiliar",
  "grade", "tela".
- **Um item por bloco funcional**, com sub-itens que o usuário reconhece na tela dele.
  Tela grande demais para um item só (>60h) se divide por função, não por arquivo.
- **Escopo negativo é obrigatório** e é onde o orçamento se protege: novas funcionalidades,
  redesenho de processo, reescrita de backend, correção de problema pré-existente,
  relatórios, migração de dados, treinamento, e tudo que já é HTML no pacote.
- **Premissas citam o que sustenta o número baixo:** backend reaproveitado, telas construídas
  sobre a infraestrutura padrão da plataforma, janelas auxiliares reaproveitadas entre telas.
- **Pontos a definir** incluem sempre: código-fonte original, confirmação de que as regras
  atuais não mudam, padrão visual, ambiente de homologação com dados representativos de todas
  as situações do fluxo, responsáveis pela homologação.

### 7. Deixar rastro

Grave em `_analise-conversao-html5/` na pasta do orçamento:

```
_analise-conversao-html5/
├── CONTEXTO.md              # inventário, modelo aplicado, riscos, pendências
├── orcamento-vN-<total>h.json
├── dados/membros-por-classe.txt
└── scripts/                 # cópia dos extratores, para reproduzir
```

Os `.txt` intermediários não precisam ser versionados — regeneram em segundos.

## O modelo

```
índice = membros + 0,5 × widgets + 2 × serviços_custom
horas  = 8h base + 0,18 × índice + 2,5h por popup
```

- **membros** — métodos e propriedades declarados nas classes do cliente. É o proxy de
  regra de negócio na tela e o termo que domina o índice.
- **widgets** — componentes MXML declarados. Peso 0,5: layout custa, mas menos que lógica.
- **serviços_custom** — chamadas distintas aos beans do addon. Peso 2: cada uma é um
  contrato a reproduzir e a homologar.
- **base 8h** — publicação, registro, i18n e fiação mínima de qualquer tela.
- **2,5h por popup** — janela auxiliar tem ciclo próprio de abrir, validar, retornar.

Calibragem e validação em `references/modelo-calibragem.md`. Resumo: aplicado ao orçamento
de Transporte (9 telas, 340h fechadas), o modelo reproduz o total das telas com **2,6% de
desvio**.

**Onde o modelo falha:** tela cuja complexidade está no backend e não no cliente (a tela é
uma casca fina sobre um bean enorme). O índice sai baixo e a homologação estoura. Sintoma:
poucos membros, muitos serviços. Quando `serviços × 10 > membros`, revisar na mão.

## Referências

- `references/modelo-calibragem.md` — derivação, validação e limites do modelo
- `references/checklist-inventario.md` — o que levantar antes de medir
- `scripts/extrai-swf-abc.py` — SWF para constant pool
- `scripts/metricas-swf.py` — métricas, índice e horas

## Orçamentos fechados com este método

| Projeto | Telas | Total | Pasta |
|---|---|---|---|
| HnzTransporteBotuvera (TMS) | 9 | 340h | `G:\Meu Drive\15. ORCAMENTOS\2985\addon transporte` |
| CotacaoW (swbcotacao) | 3 + 1 popup | 207h | `G:\Meu Drive\15. ORCAMENTOS\2985\addon cotacao` |

Consultar o `CONTEXTO.md` dessas pastas antes de estimar um addon novo — são as duas réguas.
