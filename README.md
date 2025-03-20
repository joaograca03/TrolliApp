# Trolli - Clone do Trello em Flet

Bem-vindo ao **Trolli**, um projeto desenvolvido em Python com a framework Flet, no âmbito da disciplina de Computação Móvel. Este trabalho tem como objetivo principal recriar as funcionalidades essenciais do Trello, uma ferramenta de gestão de tarefas, com a adição de melhorias e funcionalidades extra que enriquecem a experiência do utilizador e demonstram competências técnicas avançadas.

## Funcionalidades Extra e Motivação

Seguem-se as funcionalidades adicionais implementadas, com uma explicação dos motivos da sua inclusão e uma descrição técnica detalhada.

### 1. Armazenamento Local com Ficheiro JSON em Substituição do Memory Store

**Motivo da Inclusão**: Optou-se por substituir o *Memory Store* por um ficheiro JSON para garantir a persistência dos dados entre sessões da aplicação. Num cenário prático, é essencial que os utilizadores possam retomar o trabalho onde o deixaram, algo impossível com armazenamento em memória, que se perde ao encerrar o programa.

**Descrição**: A classe `JSONStore` foi implementada para gerir um ficheiro `data.json` na raiz do projeto, onde são gravados os dados de utilizadores, *boards*, listas e itens. Ao iniciar a aplicação, os dados são lidos deste ficheiro, e qualquer alteração é imediatamente sincronizada. Esta abordagem assegura que as informações sejam mantidas de forma persistente, oferecendo uma experiência mais fiável e próxima da realidade do Trello. O sistema suporta múltiplos utilizadores, organizando os dados por nome, o que facilita a expansão futura e a gestão de grandes quantidades de informação.

### 2. Remoção de Botões Não Essenciais e Substituição por "Close APP"

**Motivo da Inclusão**: A decisão de remover botões como "Archive *Boards*", "Move List" e "Settings", substituindo este último por "Close APP", visou simplificar a interface e alinhá-la com os objetivos do projeto. Estas opções foram consideradas supérfluas para um clone básico, enquanto o fecho controlado da aplicação é uma necessidade prática.

**Descrição**: Após o início de sessão, o menu da barra superior inclui a opção "Close APP", implementada com `page.window.close()`, que encerra a janela de forma imediata e controlada. A eliminação de botões irrelevantes reduz a complexidade visual, mantendo o foco nas funcionalidades principais, como a criação e gestão de *boards*. Esta alteração melhora a usabilidade e reflete uma abordagem minimalista, adequada a um projeto académico onde a clareza é prioritária.

### 3. Adição de Propriedades aos Itens das Listas (*Priority*, *Description*, *Completed* e *Tags*)

**Motivo da Inclusão**: A introdução de propriedades como prioridade, estado (*completed*) e tags foi motivada pela necessidade de enriquecer a funcionalidade das listas, tornando-as mais úteis para a gestão de tarefas. Estas características são fundamentais em ferramentas como o Trello, permitindo uma organização mais detalhada e categorização flexível das tarefas.

**Descrição**: Cada item numa lista possui agora uma prioridade ("Baixa", "Média", "Alta"), um estado, indicado por uma *checkbox* que marca a tarefa como concluída ou não, e uma lista de *tags* (ex.: "escola", "urgente") para categorização adicional. Estas propriedades são definidas no momento da criação ou edição, através de um formulário modal que inclui um campo de texto para tags separadas por vírgulas, e persistem no ficheiro JSON via `JSONStore`. A prioridade determina a cor do item na interface (verde para "Baixa", laranja para "Média", vermelho para "Alta"), enquanto o estado facilita o acompanhamento do progresso e as tags permitem agrupar tarefas por temas ou contextos específicos. Esta implementação aumenta a flexibilidade e a capacidade de organização, aproximando o Trolli de uma ferramenta profissional.

### 4. Filtros nas Listas para Pesquisa por Estado, Prioridade e Tags

**Motivo da Inclusão**: A adição de filtros, incluindo o suporte para tags, foi motivada pela necessidade de melhorar a eficiência na gestão de tarefas, especialmente em listas com muitos itens. Esta funcionalidade permite aos utilizadores localizar rapidamente tarefas específicas com base em critérios variados, um requisito comum em ferramentas de produtividade.

**Descrição**: Cada lista inclui um painel expansível com dois menus suspensos (*dropdowns*) e um botão para filtros: um *dropdown* para filtrar por estado ("Todas", "Concluídas", "Não Concluídas"), outro por prioridade ("Todas", "Baixa", "Média", "Alta"), e um botão "Selecionar Tags" que abre um diálogo com *checkboxes* para todas as tags únicas presentes na lista. A lógica em Python, implementada na classe `BoardList`, atualiza dinamicamente a visibilidade dos itens com base nas seleções combinadas. Por exemplo, selecionar "Concluídas" e a tag "escola" mostra apenas tarefas concluídas marcadas com "escola". Esta funcionalidade melhora a navegabilidade e permite uma gestão mais focada, sendo particularmente útil em cenários com grande volume de tarefas e diversas categorias.

### 5. Melhoria da Interface das Listas com Modal, Cores por Prioridade e Botão de Eliminação de Itens

**Motivo da Inclusão**: A reformulação da interface das listas foi pensada para otimizar a experiência do utilizador, escondendo o formulário de criação num modal para reduzir desordem visual, usando cores para destacar prioridades e facilitando a identificação rápida de tarefas críticas, além de permitir a remoção direta de itens para maior controlo sobre as listas. Estas melhorias tornam a gestão de tarefas mais intuitiva e eficiente.

**Descrição**: O botão "Criar Tarefa" em cada lista abre um modal com campos para nome, prioridade, descrição, tags e estado da tarefa, onde a criação só é concluída se o nome for preenchido, garantindo dados válidos. Após a criação, os itens exibem cores associadas à prioridade (verde, laranja ou vermelho), definidas na classe `Item`. Clicar num item abre um modal de edição com os detalhes, incluindo um botão "Excluir" que, ao ser clicado, apresenta um diálogo de confirmação para remover o item da lista, atualizando o `JSONStore` e exibindo uma mensagem de sucesso via `SnackBar`. Os títulos longos dos itens são cortados com reticências ("...") para manter a interface limpa, usando `ft.Text` com `max_lines=1` e `overflow=ft.TextOverflow.ELLIPSIS`. Esta melhoria torna a interface mais organizada, visualmente informativa e funcional, alinhando-se com padrões de design modernos.

### 6. Sistema de Autenticação com Registo de Utilizadores

**Motivo da Inclusão**: A implementação de um sistema de autenticação foi essencial para garantir segurança e personalização, requisitos básicos numa aplicação multiutilizador. Sem *login*, os dados seriam acessíveis a qualquer pessoa, comprometendo a privacidade.

**Descrição**: A aplicação inicia numa página de autenticação, exigindo nome de utilizador e palavra-passe. Um botão "Registar" permite criar novos utilizadores, gravando-os no JSON. Após o início de sessão, a sessão é mantida via `client_storage`, evitando autenticações repetidas. Sem *login*, o acesso às funcionalidades é bloqueado, redirecionando para a página inicial. Este sistema assegura que apenas utilizadores autenticados possam interagir com a aplicação, oferecendo uma experiência segura e personalizada.

### 7. Segregação de Dados por Utilizador

**Motivo da Inclusão**: Garantir que cada utilizador aceda apenas aos seus próprios dados foi uma decisão para replicar a confidencialidade do Trello e assegurar privacidade num ambiente multiutilizador, essencial para a credibilidade da aplicação.

**Descrição**: O `JSONStore` organiza os dados no ficheiro JSON por utilizador, associando *boards* ao respetivo nome. Após o *login*, o sistema define o `current_user`, e métodos como `get_boards()` filtram os dados para exibir apenas os pertencentes ao utilizador autenticado. Esta segregação impede que um utilizador (ex.: "joao") veja ou altere os dados de outro (ex.: "bernardo"), proporcionando segurança e uma experiência individualizada, essencial para um sistema funcional e realista.

### 8. Utilizador Administrador com Privilégios e Página "Members"

**Motivo da Inclusão**: A criação de um utilizador *admin* com uma página dedicada à gestão de utilizadores foi incluída para simular um sistema hierárquico, comum em ferramentas colaborativas, e oferecer controlo administrativo, útil num contexto académico ou profissional.

**Descrição**: Um utilizador "admin" (criado automaticamente caso não exista com palavra-passe "admin") tem acesso exclusivo à página "Members", visível no *sidebar*. Esta página lista todos os utilizadores registados, permitindo adicionar novos ou remover os existentes (exceto o "admin"). A funcionalidade é suportada por verificações no `JSONStore`, que só exibe a página se o `current_user` for "admin". Esta capacidade de gestão adiciona uma camada de administração, tornando o Trolli mais versátil e adaptado a cenários multiutilizador.

### 9. Sistema de Temas Claro e Escuro

**Motivo da Inclusão**: A introdução de temas claro e escuro foi motivada pela necessidade de melhorar o conforto visual e seguir tendências de personalização em interfaces modernas, aumentando a acessibilidade e a satisfação do utilizador.

**Descrição**: No menu superior, a opção "Dark Mode" ou "Light Mode" permite alternar entre temas, com a escolha gravada no `client_storage` para persistência. O modo escuro usa tons como `GREY_900` para o fundo, enquanto o modo claro usa `BLUE_GREY_200`, atualizados pela função `update_theme_colors()`. Esta alteração é refletida na *appbar*, *sidebar* e listas em tempo real, oferecendo uma experiência visual adaptável às preferências do utilizador e às condições de iluminação.

### 10. Sugestão Automática de Tags com NLP

**Motivo da Inclusão**: A adição de sugestões automáticas de tags foi motivada pelo desejo de facilitar a categorização de tarefas, tornando o processo mais rápido e inteligente, especialmente para utilizadores que gerem muitas tarefas ou lidam com textos em diferentes idiomas.

**Descrição**: Implementada na classe `Item`, esta funcionalidade usa a biblioteca spaCy com modelos NLP pré-treinados (`en_core_web_sm` para inglês e `pt_core_news_sm` para português) para sugerir tags a partir do título e descrição dos itens. A deteção de idioma é feita com `langdetect`, aplicando o modelo correspondente para extrair substantivos e entidades nomeadas (ex.: "Meeting with Maria" gera "meeting, maria"). No modal de edição, o botão "Sugerir Tags" adiciona até 5 tags ao campo de texto, exibindo uma notificação via `SnackBar` com o idioma detetado. Esta melhoria aumenta a produtividade e suporta multilingismo, destacando competências avançadas em NLP.

## Instruções de Utilização

### Requisitos
- Python 3.8 ou superior.
- Framework Flet: `pip install flet`.
- Bibliotecas adicionais: `pip install spacy langdetect`.
- Modelos spaCy: `python -m spacy download en_core_web_sm` e `python -m spacy download pt_core_news_sm`.

**Uso**:
- Navegue até `Trello/src/` e execute: `python main.py`.
- Inicie a aplicação e faça *login* (ex.: "admin", senha "admin") ou registe um novo utilizador.
- Crie *boards* e listas na vista "Boards".
- Adicione tarefas com o botão "Create Task", definindo título, descrição, prioridade, tags (ex.: "trabalho, urgente") e estado.
- Edite ou elimine itens clicando neles e usando os botões no modal (ex.: "Sugerir Tags" ou "Excluir").
- Use os filtros nas listas para organizar tarefas por estado, prioridade ou tags (abra o diálogo de tags para selecionar múltiplas opções).
- Altere o tema no menu superior.
- Se *admin*, aceda a "Members" para gerir utilizadores.
- Feche a aplicação com "Close App".