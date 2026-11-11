# Singleton

[← voltar](../README.md) · links fixos no commit `82162ab`

**O que é:** garante que uma classe tenha **uma única instância** e dá um ponto de acesso global a ela.

**Como se monta:**
- o construtor é **privado**, então ninguém de fora faz `new`;
- um atributo **estático** guarda a instância;
- um método **estático** `getInstancia()` cria a instância na primeira chamada e devolve sempre a mesma.

**Por que usamos:** o app inteiro precisa de **uma** conexão com o banco (um pool) e de **um** conjunto de regras de papel.

## Exemplo: BancoDeDados

Todos os repositórios chamam `BancoDeDados.getInstancia()` e recebem o mesmo objeto, com o mesmo pool de conexões.

📍 `padroes/singleton/BancoDeDados.java` · linhas 16–30 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/singleton/BancoDeDados.java#L16-L30)

```java
public class BancoDeDados {
    private static BancoDeDados instancia;

    private final JdbcTemplate jdbc;

    private BancoDeDados() {
        URI url = URI.create(Configuracao.getInstancia().getUrlDoBanco());  // postgresql://usuario:senha@host:porta/banco
        String[] usuario = url.getUserInfo().split(":", 2);
        HikariDataSource conexoes = new HikariDataSource();
        conexoes.setJdbcUrl("jdbc:postgresql://" + url.getHost() + ":" + url.getPort() + url.getPath() + "?reWriteBatchedInserts=true");
        conexoes.setUsername(usuario[0]);
        conexoes.setPassword(usuario[1]);
        conexoes.setMaximumPoolSize(4);
        jdbc = new JdbcTemplate(conexoes);
    }
```

📍 `padroes/singleton/BancoDeDados.java` · linhas 32–37 · [abrir no GitHub](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/singleton/BancoDeDados.java#L32-L37)

```java
    public static synchronized BancoDeDados getInstancia() {
        if (instancia == null) {
            instancia = new BancoDeDados();
        }
        return instancia;
    }
```

Onde é usado: [`RepositorioBase.java:14`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/compactacao/RepositorioBase.java#L14)

## Segundo exemplo

`Configuracao`, com as regras de cada papel e o endereço do motor: [`Configuracao.java:35`](https://github.com/aland3r/driftor-reuso/blob/82162ab/backend/src/main/java/br/pucpr/driftor/padroes/singleton/Configuracao.java#L35)
