# Modelo de estimativa — derivação, validação e limites

## A fórmula

```
índice = membros + 0,5 × widgets + 2 × serviços_custom
horas  = 8h base + 0,18 × índice + 2,5h por popup
```

## De onde vêm as métricas

Todas saem do **constant pool de strings** das tags `DoABC` do SWF. O compilador MXML deixa
lá, em texto claro, o caminho do arquivo-fonte, o nome de cada classe e de cada membro, e os
identificadores gerados para componentes declarados. Nada disso é ofuscado em build padrão
Flex 3.6.

| Métrica | Como é reconhecida | O que representa |
|---|---|---|
| classes do cliente | caminho de fonte contendo o workspace original e terminando em `.mxml`/`.as` | quantos arquivos a tela tem |
| membros | `[namespace:]Classe/[ns:]nome[/get\|set]`, sem prefixo `_` | métodos e propriedades — proxy de regra de negócio |
| handlers MXML | mesmo padrão, prefixo `___` | handlers inline gerados pelo compilador |
| bindings | mesmo padrão, prefixo `_` | expressões `{}` de data binding |
| widgets | `_Classe_TipoComponente<N>_i` ou `_c` | componentes MXML declarados |
| serviços custom | string começando com o domínio do `service-providers.xml` | contratos com o backend |

## Pesos — por que esses

- **membros, peso 1.** É o termo dominante e o mais fiel: cada método é comportamento que
  precisa existir na tela nova.
- **widgets, peso 0,5.** Layout custa, mas metade. `HBox`/`VBox`/`Label` viram markup quase
  direto; o custo real está no que eles disparam, que já entrou como membro.
- **serviços, peso 2.** Cada chamada distinta é um contrato: formato de requisição, formato
  de retorno, tratamento de erro, e um caso de homologação.
- **base 8h.** Piso de qualquer tela: registro no menu, launcher, i18n, permissão, publicação.
  Nenhuma tela custa menos que isso, por trivial que seja.
- **fator 0,18.** Calibrado, não derivado. Ver abaixo.
- **2,5h por popup.** Janela auxiliar tem ciclo próprio — abrir com contexto, validar,
  devolver resultado para a tela-mãe.

## Como o fator 0,18 foi calibrado

Régua: a tela `ControlePneus` do addon HnzTransporteBotuvera, **efetivamente convertida** para
HTML5 no padrão sankhya-js AngularJS. Entrega real: ~1.346 linhas (JS 714, HTML 183, CSS 31,
4 popups), consumindo o bean `ControlePneusSP` sem recompilar o EJB.

Uma primeira versão do modelo (`12h base + 0,30 × índice + 4h/popup`) produzia 65h para essa
tela e 558h para o pacote de 9 telas. Coerente com as linhas entregues, mas alto para telas
que, olhando o inventário, são **personalização sobre DynamicForm** e não telas desenhadas do
zero — e que reaproveitam janelas auxiliares entre si.

A recalibragem para `8h + 0,18 × índice + 2,5h/popup` assume esses dois ganhos e foi a versão
fechada com o cliente em 340h.

## Validação cruzada — Transporte

Modelo aplicado aos 10 SWF do HnzTransporteBotuvera, comparado ao orçamento fechado:

| Tela | Script | Orçamento | Desvio |
|---|---|---|---|
| OrdemCargaBot | 90,8 | 90 | +0,8 |
| FechamentoViagem | 23,7 | 22 | +1,7 |
| OrdensCarregamento | 20,6 | 20 | +0,6 |
| Rotas | 19,9 | 20 | −0,1 |
| Pedidos | 19,6 | 24 | −4,4 |
| ApontamentoTerceiros | 19,3 | 18 | +1,3 |
| PneusPanel | 14,9 | 10 | +4,9 |
| RomaneioEntrada | 14,1 | 14 | +0,1 |
| LancamentosContabeisPanel | 11,1 | 10 | +1,1 |
| **Soma (excl. ControlePneus)** | **234,0** | **228** | **+2,6%** |

`ControlePneus` (39,8h pelo script) ficou fora por já estar convertida.

Os dois maiores desvios são explicáveis e ambos foram ajuste manual consciente:

- **Pedidos** subiu de 19,6 para 24 porque o filtro tem 9 componentes de pesquisa e duas abas
  reaproveitadas de outra tela — o índice não capta o custo de aba.
- **PneusPanel** caiu de 14,9 para 10 porque seu único popup (`PopUpGerarNumeros`) **já existia
  convertido** como `PopUpNumeroFogo.js`.

Ou seja: o modelo acerta o agregado, e os desvios individuais vêm de reuso e de estrutura
que o constant pool não expõe. Por isso a etapa 4 do fluxo existe.

## Validação — Cotação

| SWF | Script | Orçamento | Observação |
|---|---|---|---|
| RotinaCotacao | 102,7 | 105 | script contou 4 popups; `Preferencias` não casa `^Popup` → +2,5h |
| ModeloEmail | 12,0 | 12 | — |
| PesoCadastro | 9,8 | 10 | — |
| PopupProdutos avulso | 19,7 | 4 | **mesma classe já orçada dentro de RotinaCotacao** — só registro |

O caso `PopupProdutos` é o exemplo canônico de por que não se aceita o total bruto: a classe
aparece em dois SWF e o script a conta duas vezes. Aceitar os 19,7h seria cobrar duas vezes
pelo mesmo componente.

## Limites conhecidos

**Casca fina sobre bean gordo.** Se a regra mora no backend e a tela só desenha, o índice sai
baixo e a homologação estoura. Sintoma numérico: `serviços × 10 > membros`. Revisar na mão.

**Aba e sub-tela não têm peso próprio.** `viewStack`, `Accordion` e `TabNavigator` aparecem
como um widget só, mas cada aba é um contexto de tela. Se a tela tem mais de 3 abas com
formulário próprio, some 4–6h por aba além da primeira.

**Detecção de popup é heurística.** Só casa `^Popup`/`^PopUp`. Janela auxiliar chamada
`Preferencias`, `Configuracoes`, `Wizard*` ou `*Dialog` passa batido.

**SQL embutido não entra no índice.** A tela pode carregar critérios SQL no cliente
(`EXISTS(SELECT ...)` em filtro). É trabalho de conversão real. Se houver mais de 15 trechos,
some 4–8h.

**Não cobre mudança de padrão.** O modelo pressupõe sankhya-js AngularJS sem pipeline Node.
Design System (`ez-`/`snk-`, Vite) muda o custo: multiplicar desenvolvimento por ~1,4 e somar
setup de build.

**Não cobre reescrita de backend.** Se o bean precisar mudar além do formato de retorno, o
modelo inteiro é inválido — estime o backend com `sankhya-estimativa-planejador`.

## Ajuste do fator, se necessário

Ao fechar uma conversão, compare horas apontadas contra estimadas por tela e recalcule:

```
fator_novo = (horas_reais − 8 − 2,5 × popups) / índice
```

Média dos fatores por tela, descartando os dois extremos. Registre a nova calibragem aqui,
com o projeto de origem — o valor 0,18 vale para addon Sankhya sobre infraestrutura padrão de
tela, não para tela desenhada do zero.
