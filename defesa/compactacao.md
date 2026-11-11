# Compactação de código

[← defesa](README.md) · links fixos no commit `21ee145`

**Técnica:** extrair para uma **superclasse** o código que se repetia em várias classes (Extract Superclass / Pull Up Method). As subclasses herdam e ficam só com o que é delas.

**Onde:** os quatro repositórios tinham os mesmos `listar`, `obter` e `excluir`, só mudando a tabela e as colunas. Esses métodos subiram para `RepositorioBase`. Cada repositório agora só informa a tabela, as colunas e como uma linha vira objeto.

- **Antes:** commit [`a7fd19b`](https://github.com/aland3r/driftor-reuso/blob/a7fd19b/backend/src/main/java/br/pucpr/driftor/atividade/AtividadeRepositorio.java)
- **Depois:** commit [`82162ab`](https://github.com/aland3r/driftor-reuso/commit/82162ab)

📍 `compactacao/RepositorioBase.java` · linhas 13–40 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/compactacao/RepositorioBase.java#L13-L40)

```java
public abstract class RepositorioBase<T> {
    protected final BancoDeDados banco = BancoDeDados.getInstancia();
    private final String tabela;
    private final String colunas;
    private final String ordem;

    protected RepositorioBase(String tabela, String colunas, String ordem) {
        this.tabela = tabela;
        this.colunas = colunas;
        this.ordem = ordem;
    }

    protected abstract T criarObjeto(ResultSet linha) throws SQLException;

    // ---- Read
    public List<T> listar() {
        return banco.consultar("select " + colunas + " from " + tabela + " order by " + ordem, (linha, n) -> criarObjeto(linha));
    }

    public T obter(UUID id) {
        return banco.consultar("select " + colunas + " from " + tabela + " where id = ?", (linha, n) -> criarObjeto(linha), id).get(0);
    }

    // ---- Delete
    public void excluir(UUID id) {
        banco.executar("delete from " + tabela + " where id = ?", id);
    }
}
```

Uma subclasse, depois da compactação:

📍 `atividade/AtividadeRepositorio.java` · linhas 10–19 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/21ee145/backend/src/driftor/atividade/AtividadeRepositorio.java#L10-L19)

```java
public class AtividadeRepositorio extends RepositorioBase<Atividade> {

    public AtividadeRepositorio() {
        super("atividades", "id, nome", "nome");
    }

    @Override
    protected Atividade criarObjeto(ResultSet linha) throws SQLException {
        return new Atividade(linha.getObject("id", UUID.class), linha.getString("nome"));
    }
```

## Roteiro do vídeo (até 3 minutos, não listado no YouTube)

1. Abrir o commit **antes** (`a7fd19b`) em `AtividadeRepositorio.java` e `ProcessoRepositorio.java`. Mostrar que os dois têm `listar`, `obter` e `excluir` iguais, só com outra tabela.
2. Abrir o diff do commit **depois** (`82162ab`). Mostrar que esses métodos saíram dos quatro repositórios.
3. Abrir `RepositorioBase.java` e explicar: a tabela, as colunas e a ordem vêm pelo construtor, e `criarObjeto` é o único método que cada repositório escreve.
4. No site, criar, renomear e excluir uma atividade para mostrar que continua funcionando.
