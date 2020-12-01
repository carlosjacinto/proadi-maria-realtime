# 1. Visão Geral

Para que seu modelo seja submetido no módulo de Gerenciamento Automatizado para Sistemas de Predição em Real-time (GASPR) é necessário seguir o padrão descrito neste documento. Este padrão foi definido com o objetivo de simplificar ao máximo o trabalho dos cientistas e pesquisadores envolvidos ao adaptar os modelos já desenvolvidos para execução em nossa plataforma.

## Recursos disponíveis para execução
    
Cada modelo é encapsulado em um ambiente isolado via containers. A configuração padrão utilizada é:

- Debian GNU/Linux 10 (buster)
- Imagem Docker Python

# 2. Bundle de submissão
    
Para que seu modelo de Machine Learning (ML) seja submetido é necessário estruturá-lo em um formato de “bundle”. Este bundle consiste em um arquivo compactado (“.zip”) que possui todos os arquivos necessários para a execução do modelo. **Seu modelo deve ser capaz de ser executado em um ambiente Docker com imagem Python na versão escolhida pelo pesquisador**.

Os arquivos mínimos necessários para a execução em nossa plataforma são:

### Arquivo "requirements.txt":
    

Arquivo com lista de bibliotecas necessárias para a execução do modelo. Como a instalação dessas libs serão realizadas via gerenciador de pacotes PIP é necessário seguir o mesmo padrão. Para verificar releases dos pacotes presentes e mais informações acesse [https://pypi.org/](https://pypi.org/).

Não existe qualquer restrição de quantidade ou tipos de arquivos presentes no bundle além dos obrigatórios descritos anteriormente. Dessa forma tenha liberdade para adicionar qualquer arquivo que seu código necessite (scripts, etc). Se porventura alguma biblioteca utilizada não esteja presente no gerenciador de pacotes PIP você também pode inclui-lá no seu bundle e importá-la utilizando caminhos relativos.

### Arquivo "predict.py":

Um script escrito em Python que deve receber uma entrada como argumento e retornar a predição final.

Esse script deve ser capaz de receber três argumentos de entrada:

|Parâmetro|Descrição|
|--|--|
|--exam_path|Contém uma string com o diretório o qual todo o exame (imagens e metadados) estarão disponíveis para leitura (mais detalhes na seção Padrão de Entrada).|
|--exam_data|Contém uma string com o caminho até o arquivo JSON com metadados e outras informações relevantes do exame (mais detalhes na seção Padrão de Entrada).|
|--model_output|Contém uma string com o caminho em que as saídas do modelo devem ser salvas (mais detalhes na seção Padrão de Entrada).|

### Resultados do modelo:

A saída esperada do modelo deve ser um arquivo JSON com informações obrigatórias e não obrigatórias definidas para o pesquisador no padrão de saída do bundle. A quantidade de arquivos de JSON com predição e os nomes dos arquivos são de livre escolha do pesquisador. Todos os arquivos com extensão JSON dentro da pasta informada na parâmetro “model_output” será analisado como uma possível predição do exame.

```sh
├── exemplos
│   ├── Dockerfile.dev
│   ├── inputs
│   ├── model
│   ├── outputs
│   ├── teste.py
│   └── worker_requirements.txt
└── README.md
```

# 3. Padrão de entrada

O exame será disponibilizado para o modelo a partir de um arquivo de metadados e uma hierarquia de diretórios contendo todas as imagens relacionadas ao exame.

## Metadados

Alguns metadados estarão disponíveis para os modelos através do arquivo JSON no caminho fornecido pelo argumento “--exam_data” com o objetivo de agilizar o acesso aos mesmos sem a necessidade de abrir os arquivos do exame. Entretanto, é importante frisar que todos os metadados originais continuam disponíveis nos arquivos DICOM e podem ser acessados e manipulados de forma tradicional.

O padrão adotado para o arquivo JSON de metadados é:

```javascript
{
  "study_description": "Descrição do estudo",
  "study_id": "ID do estudo",
  "aquisition_date": "Data de aquisição do exame",
  "modality": "Lista de todas as modalidades existentes no exame",
  "n_series": "Número de séries que o exame possui",
  "series": [
    {
      "series_id": "Identificador da série",
      "modality": "Modalidade da série",
      "body_part": "Parte do corpo em que o exame foi realizado",
      "procedure": "Procedimento realizado",
      "n_images": "Total de imagens da série",
      "instance_ids": "lista com o código das imagens DCM"
    }],
  "birthDate": "Data de nascimento do paciente Padrão YYYY-MM-DD",
  "gender": "Sexo do paciente (female ou male)",
  "age": "Idade do paciente no momento do exame",
  "patient_height": "Altura do paciente",
  "patient_weight": "Peso do paciente",
  "image_height": "Quantidade de linhas de cada imagem",
  "image_width": "Quantidade de colunas de cada imagem",
  "bits_per_pixel": "Quantidade de bits em cada pixel da imagem",
  "lossy_compression": "Se a imagem passou por alguma compressão com perdas",
  "pixel_spacing": "Espaçamento dos pixels",
  "slice_thickness": "Espessura das fatias"
}
```

Como visto no template anterior o modelo terá acesso a informações básicas do exame e das séries permitindo identificar quais modalidades e/ou procedimentos a serem analisados. É de responsabilidade do modelo manipular esses dados corretamente e identificar quais imagens devem ser processadas ou não.

## Imagens

As séries presentes no exame serão disponibilizadas aos modelos por meio de uma hierarquia de arquivos locais, ou seja, toda a responsabilidade de organização dos arquivos do exame pertence ao módulo de execução e não ao modelo enviado pelo pesquisador.

Todas as imagens presentes no diretório estarão com formato do tipo DICOM.
Os arquivos serão organizados dentro do diretório identificado pelo argumento `--exam_path` em pastas com o id de cada série como apresentado na figura abaixo:

```sh
Colocar o outro aqui, Carlinhos!
```

Cabe ao modelo identificar quais séries ele deseja consumir e acessar o diretório seguindo o padrão **“EXAM_PATH/SERIES_ID”**.

$ 4. Padrão de saída

As saídas dos modelos devem ser salvas como arquivos JSON no diretório do argumento `--model_output` seguindo a estrutura apresentada abaixo:

```javascript
{
  "scope": “Escopo da resposta da predição: study, series ou instance (Obrigatório)",
  "study_id": “Identificador do estudo (Obrigatório)",
  "series_id": “Identificador da série (Com base na regra abaixo)",
  "instance_id": "Identificador da imagem (Com base na regra abaixo)",
  "model_output": "Lista de resultados do modelo (Obrigatório)",
  "files": "Lista de arquivos (caminhoRelativo/imagem.extensão) que o usuário deseja enviar para o usuário final (Opcional)"
}
```