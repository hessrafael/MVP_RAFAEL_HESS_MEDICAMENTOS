 # API Medicamentos

Este projeto python (v.3.10.6) é para um sistema de gestão de medicamentos em um hospital. Ele deve ser usado em conjuntos com os seguintes sistemas localizados em https://github.com/hessrafael/MVP_RAFAEL_HESS_PACIENTES e https://github.com/hessrafael/MVP_RAFAEL_HESS_PROCEDIMENTOS

---
## Executando com o Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t medic_api .
```

Para comunicação entre os microsserviços associados, cria-se uma rede comum entre eles, executando (caso ainda não tenha criado), **como administrador**, o seguinte comando:

```
$ docker network create --driver=bridge med-net
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -d --name=med-cont --net=med-net -p 5001:5001 medic_api
```

Uma vez executando, para acessar a API, basta abrir o [http://localhost:5001/#/](http://localhost:5001/#/) no navegador.

---
## Como executar sem o Docker (ambiente de desenvolvimento)

Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.

Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenpython).

Para criar o ambiente virtual execute o seguinte comando:

```
python -m venv env
```
Navegue até o diretório com o seguinte comando:

```
cd .\env\Scripts  
```
E ative o ambiente rodando:

```
.\activate
```

o comando a seguir instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`. Navegue até o diretório ".\api" e execute:

```
(env)$ pip install -r requirements.txt
```

Para executar a API  basta executar no diretório ".\api":

```
(env)$ flask run --host 0.0.0.0 --port 5001
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor
automaticamente após uma mudança no código fonte. 

```
(env)$ flask run --host 0.0.0.0 --port 5001 --reload
```

Abra o [http://localhost:5001/#/](http://localhost:5001/#/) no navegador para verificar o status da API em execução.

---
## Executando os testes funcionais

Para executar os testes funcionais, esteja com o ambiente virtual ativo

Navegue até o diretório ".\api" e execute:

```
(env)$ python -m pytest -v --disable-warnings
```

