# Checklist de inventário — antes de medir

Percorrer inteiro antes de rodar qualquer script. Cada linha não respondida vira um "ponto a
definir" no orçamento ou uma hora não cobrada.

## Identificação do pacote

- [ ] `extension.xml` — id, versão, data de build, vendor, módulo licenciado
- [ ] É **addon de produto Sankhya** ou **customização de cliente**? Muda o interlocutor,
      a régua de escopo negativo e quem decide o que sai
- [ ] Existe repositório do fonte Flex? O caminho está embutido no SWF
      (`...workspace\<versão>\<Nome>-VC-Flex\src`). Pedir. É a maior alavanca de redução
- [ ] Existe fonte Java do EJB, ou só `.class`?

## Telas

- [ ] Listar `web/<ctx>/flex/*.swf`, descartando `framework_*.swf` e `playerProductInstall.swf`
- [ ] Para cada SWF: já existe equivalente em `web/<ctx>/html5/`? Se sim, **fora do escopo**
- [ ] Alguma tela do módulo já foi convertida? É régua interna — cita no orçamento e reduz risco
- [ ] Há classe repetida entre SWF? Construir uma vez, publicar N vezes

## Launcher e configuração

- [ ] `launcher/*.body` — quais `configuracaoTela` a tela lê
- [ ] `launcher/*.i18n` — **contar as chaves**. Acima de 150, o item de estrutura sobe
- [ ] `launcher/*.parameters` — cada parâmetro é um caminho de comportamento a reproduzir
      e a homologar
- [ ] `<addon>/ejb/*.jar` → `parameters/parameter.xml` — parâmetros declarados e seus defaults

## Backend

- [ ] `WEB-INF/resources/service-providers.xml` — domínios e beans expostos
- [ ] Tamanho dos `.class` dos helpers. Bean grande (>50 KB de bytecode) e tela pequena
      é o sinal de "casca fina sobre bean gordo" — o modelo subestima
- [ ] Listeners e jobs no jar — não entram na conversão, mas afetam homologação
- [ ] Provider DWF próprio (`*-dwf.xml`) e seus descritores
- [ ] O bean expõe retorno em XML acoplado ao cliente Flex? Se sim, item (c) sobe

## O que já é HTML

- [ ] Existe portal, tela html5 ou aplicação web separada no pacote?
- [ ] Contar linhas e stack. Vai para **escopo negativo**, com a frase de que já é aplicação
      web e não depende da tecnologia descontinuada
- [ ] Se o cliente pedir modernização das libs, é escopo separado — estimar à parte, nunca
      embutir

## Dados

- [ ] `datadictionary/metadata.xml` — campos e tabelas. Conversão de tela **não** mexe aqui;
      serve para afirmar no escopo negativo que não há alteração de estrutura
- [ ] `dbscripts/*.sql` — objetos criados pelo addon. Mesma finalidade

## Integrações externas

- [ ] A tela conversa com serviço de terceiro (operadora, SEFAZ, balança, gateway)?
- [ ] Cada integração exige ambiente e credencial de homologação → **ponto a definir** e
      risco de suspensão do cronograma
- [ ] Alguma integração está descontinuada? Sai do escopo e reduz horas — perguntar

## Fluxo e situações

- [ ] Quais são os estados possíveis do registro principal? (ex.: `STATUSPRODCOT` com
      `O/E/P/A/C/F`)
- [ ] O ambiente de homologação tem dado representativo de **todos** eles? Vira premissa
- [ ] Quantas abas / sub-telas por `viewStack` ou `Accordion`? Acima de 3 com formulário
      próprio, somar 4–6h por aba além da primeira

## Padrão de tela alvo

- [ ] sankhya-js AngularJS (`angular.module('X', ['snk'])`, sem Node) — **assumido por padrão**
- [ ] Design System (`ez-`/`snk-`, npm/Vite) — se for, multiplicar desenvolvimento por ~1,4
      e somar setup de build
- [ ] Confirmar com o cliente. Se não confirmado, entra como premissa explícita: "as horas
      consideram o padrão X; padrão diferente exige revisão do orçamento"
