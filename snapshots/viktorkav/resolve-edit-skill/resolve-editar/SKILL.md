---
name: resolve-editar
description: Use ao montar ou revisar um vídeo de fala no DaVinci Resolve, selecionando tomadas, fazendo o corte inicial, ajustando a voz e inserindo apoios já disponíveis numa timeline editável.
---

# Editar no DaVinci Resolve

Entregue uma montagem editável, com fala coerente, sincronismo preservado e apoios que ajudem a entender o conteúdo. A gravação determina o que foi dito; o roteiro, quando existir, ajuda a localizar a intenção. Adapte o rigor dos cortes e o ritmo ao pedido e à performance de quem fala.

Esta skill é um procedimento. Ela não instala o Resolve, um conector MCP, um transcritor ou plugins. Use os recursos realmente disponíveis; não dependa de identidade visual, preset de áudio ou modelo específico de transcrição.

## Preparar o acesso

1. Identifique o projeto e a timeline de destino, os brutos, a voz principal e o resultado pedido. Reaproveite mídia importada, transcrição e sincronismo já conferidos. Se houver ambiguidade entre projetos ou timelines, esclareça o destino antes de editar.
2. Consulte os conectores MCP disponíveis para Resolve e leia suas ferramentas e argumentos. Teste a conexão com uma leitura do projeto, da timeline e de suas propriedades. O nome de uma ferramenta não comprova que ela consegue cortar, tratar áudio ou salvar.
3. Sem um MCP funcional, use a API oficial de scripting da Blackmagic Design, se acessível no ambiente. Abra a documentação da **versão instalada** em `Help > Documentation > Developer`; consulte o README, as definições da API e os exemplos. O [guia oficial da Blackmagic](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20.2_New_Features_Guide.pdf) também indica esse local para a documentação de desenvolvimento.
4. Confira versão, edição Free/Studio, sistema e runtime suportado. Para scripting externo, verifique a preferência de acesso correspondente; em versões que oferecem `Preferences > System > General > External scripting`, use `Local` para um processo na mesma máquina. Não habilite acesso de rede para resolver uma conexão local. Configure módulos, biblioteca e variáveis de ambiente somente conforme a documentação instalada; algumas versões fornecem runtime próprio.

Este exemplo faz apenas uma leitura, depois que o acesso estiver configurado. Não o execute com um Python escolhido sem conferir sua compatibilidade:

```python
if "resolve" not in globals() or resolve is None:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
if resolve is None:
    raise RuntimeError("Conexão com o Resolve indisponível")
manager = resolve.GetProjectManager()
project = manager.GetCurrentProject()
if project is None:
    raise RuntimeError("Nenhum projeto aberto")
timeline = project.GetCurrentTimeline()
if timeline is None:
    raise RuntimeError("Nenhuma timeline selecionada")
print(project.GetName(), timeline.GetName())
```

Não afirme que a preparação terminou até obter um retorno válido. Se faltar aplicação, licença compatível, acesso ou uma operação essencial, explique o requisito concreto. Avance na leitura e no planejamento que forem possíveis; deixe identificada a ação que depende de controle manual. A [central oficial da Blackmagic](https://www.blackmagicdesign.com/support) fornece instaladores e manuais.

## Preservar a montagem

Leia a timeline antes de alterá-la: duração, FPS, timecode inicial, pistas, clipes, mídia offline, efeitos e ajustes existentes. Não mude FPS, resolução ou gerenciamento de cor apenas para facilitar a automação.

Salve o projeto e duplique a timeline com um nome reconhecível e sem colisão. Confira que a cópia contém a montagem e os ajustes esperados. Por padrão, trabalhe na cópia e preserve a original como checkpoint; respeite outro destino explicitamente pedido. Se a duplicação falhar, resolva a recuperação antes de fazer alterações destrutivas. Uma cópia de timeline não substitui os brutos nem um backup do projeto.

Em uma retomada, comece pela montagem atual. Preserve decisões manuais e confira o que já foi executado antes de importar mídia, reaplicar efeitos ou reinserir apoios. Após falha ou retorno incerto de uma operação, releia a timeline antes de repeti-la.

## Decupar pela fala

Transcreva a voz principal com a ferramenta disponível, ou use uma transcrição existente cuja origem e tempos sejam conhecidos. A transcrição serve para busca; escute as passagens que determinam a escolha e as bordas dos cortes. Se ela estiver errada ou incompleta, a gravação prevalece.

Para cada ideia, localize tentativas completas, erros, abandonos e retomadas, inclusive quando a repetição estiver distante. Escolha por sentido, clareza e performance, sem favorecer automaticamente a última tentativa. Preserve improvisos úteis, ressalvas, números, negações e pausas que sustentem a explicação.

Remova uma repetição quando houver evidência de que ela é uma nova tentativa da mesma fala. Uma frase parecida também pode ser reforço intencional. Detecção de silêncio pode sugerir pontos de revisão; não use limiar de pausa como decisão automática de corte. Não invente palavras para fazer a gravação coincidir com o roteiro.

Mantenha um mapa simples das escolhas: intenção, arquivo de origem, entrada e saída, posição na montagem e motivo de descarte quando relevante. Distingua o relógio da fonte do relógio da timeline. Use o FPS real de cada um e confira a convenção de entrada/saída da ferramenta, evitando arredondamentos que cortem sílabas ou criem lacunas. Dúvidas que não possam ser resolvidas pela escuta ficam marcadas com timecode.

## Fazer o corte inicial

Monte uma sequência compreensível, com as ideias completas e transições naturais. Corte erros e tentativas abandonadas; ajuste excessos de preparação e espera sem acelerar indiscriminadamente a fala. Escute alguns segundos antes e depois de cada corte difícil.

Se a voz vier de outra fonte, confirme offset e possível drift ao longo da gravação. Corte e mova vídeo e voz juntos, preservando o vínculo quando a ferramenta permitir. Evite manter o áudio da câmera junto da voz principal sem intenção, causando duplicação ou faseamento.

Mantenha acesso aos arquivos originais e às alternativas. Ajuste enquadramentos apenas quando ajudarem a leitura, dentro da resolução disponível e do estilo pedido. A primeira montagem não exige animações, transições ou efeitos de câmera para estar concluída.

## Ajustar a voz

Confira canais, roteamento, ganho, picos e ruído antes de aplicar processamento. Busque inteligibilidade e nível consistente com os recursos nativos disponíveis. Use equalização, compressão e redução de ruído somente quando a gravação justificar, ouvindo possíveis artefatos e preservando a naturalidade. Não aplique uma cadeia fixa nem prometa corrigir clipping já gravado.

Prefira ajustes reversíveis. Se um controle não estiver exposto pelo conector ou pela API, execute pela interface disponível ou indique a etapa manual pendente; não simule sucesso. Compare antes/depois em volume semelhante e confira o resultado também nos cortes.

Não processe a mesma voz duas vezes. Se criar um bounce com efeitos incorporados, confira sincronismo e desative os efeitos equivalentes na cadeia ativa. Preserve a fonte e mantenha apenas a versão escolhida na reprodução. Use crossfades curtos quando necessários para eliminar cliques, sem sobrepor palavras.

## Inserir apoios disponíveis

Faça esta etapa quando houver b-roll solicitado e arquivos utilizáveis. Inventarie conteúdo, versão, duração e FPS; reaproveite itens do Media Pool sem duplicar importações. Nome de arquivo sugere um assunto, mas não comprova onde o apoio deve entrar.

Ancore cada apoio na ocorrência correta da fala **da montagem atual**, depois dos cortes e reordenações. Confira a imagem e a escuta quando a mesma frase aparecer mais de uma vez. Se a fala correspondente foi removida, deixe o apoio fora; não recoloque a fala para acomodá-lo.

Insira em pistas de vídeo adequadas à composição, preservando narração e duração da montagem. Use somente vídeo quando o som do arquivo for incidental. Inclua o áudio do apoio quando fizer parte da intenção, com nível compatível com a voz. Deixe tempo para ler telas e entender ações; retorne ao apresentador em reações, mudanças de assunto e ênfases que dependam dele.

Quando o apoio for curto, procure outro trecho ou reduza a cobertura. Retiming pode ajudar se preservar o sentido e a legibilidade; não estique a narração para preencher uma imagem. Respeite elementos manuais já presentes e confira sobreposições antes de inserir.

## Conferir e entregar

Releia a estrutura final e revise imagem e som: começos e finais de falas, cortes, sincronismo no início/meio/fim, lacunas, mídia offline, voz duplicada, clipping, apoios e leitura de textos. Metadados da API não substituem a revisão audiovisual; informe quando ela não puder ser realizada.

Compare a duração antes/depois e explique diferenças inesperadas. Inserir apoios sobre o corte aprovado deve preservar sua duração; se ela mudou, procure clipes deslocados ou anexados ao fim. Confira que o encerramento não foi truncado e que não ficaram sobras acidentais depois dele.

Salve e verifique o retorno da operação. Quando houver destino disponível e a ferramenta permitir, exporte uma cópia recuperável do projeto ou da timeline e confira a existência do arquivo. Um export de projeto/timeline não inclui necessariamente a mídia. Renderize um vídeo final somente quando essa entrega tiver sido pedida.

Informe projeto, timeline de trabalho, checkpoint, duração e o que foi realmente concluído. Localize pendências por timecode, distinguindo dúvidas editoriais de limitações técnicas. Preserve brutos, fontes e alterações anteriores; remova apenas temporários próprios que não sejam necessários à recuperação.
