---

Recomendação de Filmes
Tech Challenge 03 - MLET3

---

Dataset Utilizado

Para gerar as recomendações, utilizamos um dataset robusto com diversas features disponíveis no Kaggle: The Movies Dataset.

**Principais informações sobre o dataset:**

* 45.000 filmes listados no Full MovieLens Dataset (até julho de 2017).
* Metadados: elenco, equipe, palavras-chave, orçamento, receita, pôsteres, datas de lançamento, idiomas, estúdios, países, votos e avaliações do TMDB ([https://www.themoviedb.org/](https://www.themoviedb.org/)).
* 26 milhões de avaliações de 270.000 usuários (notas de 1 a 5, obtidas do GroupLens).

---

Tipos de sistemas de recomendação utilizados

1.  **Baseado em Popularidade:** Recomenda filmes que foram mais visualizados, comprados e bem avaliados.
2.  **Baseado em Conteúdo:** Compara características dos filmes para sugerir títulos similares.
3.  **Abordagem Híbrida:** Combina filtragem colaborativa, baseada em conteúdo e outras estratégias para gerar recomendações mais precisas.

---

Versões Testadas

1.  Similaridade usando apenas palavras-chave.
2.  Popularidade baseada nas avaliações mais altas.
3.  Similaridade combinando título, gênero e palavras-chave.

---

Versão final

Utilizamos uma abordagem híbrida:

* **Sistema baseado em similaridade de conteúdo:** Utilizando título, gênero e palavras-chave.
* **Sistema baseado em popularidade:** Considerando a nota e a quantidade de votos.

**Resultado final:**

Score final baseado em 70% similaridade e 30% popularidade.

Web App:
https://techchallenge03.streamlit.app/

---

Banco de dados

Para garantir eficiência na recuperação e armazenamento dos dados, realizamos as seguintes etapas:

* **Criação das tabelas:** Utilizando os dados de similaridade e dos filmes em CSV, estruturamos o banco de dados.
* **Importação dos dados:** Inserimos os dados dos filmes e suas características.
* **Otimização e indexação:** Implementamos índices para melhorar a performance das consultas e reduzir o tempo de resposta do sistema.

### Configurações da Instância do Banco de Dados

* **Servidor:** Hospedado pelo serviço RDS da AWS.
* **Banco de Dados:** PostgreSQL.
* **Especificações da Instância:**
    * 2 CPUs
    * 4GB RAM
    * 20GB SSD


Script de Criação e Carga:
https://www.mediafire.com/file/xnwd2ukctozmopg/techchallenge_03_database.sql/file
---

Visualização

Criamos um sistema de recomendação utilizando Streamlit, no qual o usuário pode escolher um filme e visualizar os filmes recomendados com base na abordagem híbrida.

A conexão com o banco de dados foi feita de forma direta utilizando SQLAlchemy.

Para recuperarmos os pôsteres dos filmes, realizamos a utilização da API do TMDB.
