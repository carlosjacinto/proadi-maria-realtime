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

#### Esse script deve ser capaz de receber três argumentos de entrada:

|Parâmetro|Descrição|
|--|--|
|--exam_path|Contém uma string com o diretório o qual todo o exame (imagens e metadados) estarão disponíveis para leitura (mais detalhes na seção Padrão de Entrada).|
|--exam_data|Contém uma string com o caminho até o arquivo JSON com metadados e outras informações relevantes do exame (mais detalhes na seção Padrão de Entrada).|
|--model_output|Contém uma string com o caminho em que as saídas do modelo devem ser salvas (mais detalhes na seção Padrão de Entrada).|

#### Esse script deve ser capaz de produzir como resposta:

A saída esperada do modelo deve ser um arquivo JSON com informações obrigatórias e não obrigatórias definidas para o pesquisador no padrão de saída do bundle. A quantidade de arquivos de JSON com predição e os nomes dos arquivos são de livre escolha do pesquisador. Todos os arquivos com extensão JSON dentro da pasta informada na parâmetro “model_output” será analisado como uma possível predição do exame.

```sh
model/
├── APModel
│   ├── cfg_ap.json
│   └── weight_ap.ckpt
├── ARModel
│   ├── cfg_ar.json
│   └── weight_ar.ckpt
├── predict.py
├── requirements.txt
├── src
│   ├── data_utils
│   │   ├── dataset.py
│   │   ├── imgaug.py
│   │   ├── IngestModule.py
│   │   ├── misc.py
│   │   ├── ModelOutput.py
│   │   ├── OutputModule.py
│   │   └── utils.py
│   └── model_utils
│       ├── APEngine.py
│       ├── AREngine.py
│       ├── attention_map.py
│       ├── backbone
│       │   └── densenet.py
│       ├── classifier.py
│       ├── global_pool.py
│       ├── PostProcessingModule.py
│       ├── TPEngine.py
│       └── utils.py
└── TPModel
    ├── cfg_tp.json
    └── weight_tp.ckpt

```
> Exemplo de estrutura de um bundle válido para o sistema Real Time.

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
inputs/
├── 1.3.46.670589.30.1.6.1.963334367394.1596547172859.1
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.1.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.2.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.3.dcm
│   └── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.4.dcm
├── 1.3.46.670589.30.1.6.1.963334367394.1596547172859.2
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.1.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.2.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.3.dcm
│   └── 1.3.46.670589.30.1.6.1.963334367394.1596547172937.4.dcm
├── 1.3.46.670589.30.1.6.1.963334367394.1596547179625.1
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.1.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.2.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.3.dcm
│   └── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.4.dcm
├── 1.3.46.670589.30.1.6.1.963334367394.1596547179625.3
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.1.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.2.dcm
│   ├── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.3.dcm
│   └── 1.3.46.670589.30.1.6.1.963334367394.1596547179734.4.dcm
└── exam_data.json
```
> Estrutura de um exame.

Cabe ao modelo identificar quais séries ele deseja consumir e acessar o diretório seguindo o padrão **“EXAM_PATH/SERIES_ID”**.

# 4. Padrão de saída

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

Algumas observações acerca dos campos:

- “scope”: Valor deve ser study, series ou instance.
- “series_id”: Obrigatório informar caso o campo scope seja serie ou - instance.
- “instance_id”: Obrigatório informar caso o campo scope seja instance.
- “files”: Não existe regra para a quantidade ou extensão dos arquivos.
- “model_output”: Lista de objetos contendo os campos abaixo:
  - “type”: Valor deve ser "binary", "heatmap", "freeform", “point”, “line”, “polygon” ou "bbox"; 
  - “label_id”: Tag do resultado (de acordo com o cadastro de Labels);
  - “data”: Objeto contendo o resultado, deve conter os campos seguindo o padrão abaixo:

O campo “model_output” pode possuir N objetos de cada tipo (Detalhados abaixo).

Deve-se preencher esses campos de forma diferente dependendendo do escopo que o resultado do modelo contempla. Os escopos disponíveis são:

## Resultado para todo o exame

Caso o resultado do modelo contemple todo o exame, o JSON de saída deve ser gerado preenchendo todos os campos apresentados anteriormente com os identificadores corretamente preenchidos (ids), porém deixando o campo “series_id” e “instance_id” como nulos.
Exemplo:
```javascript
{
    "scope": "study",
    "study_id": "00000.00000.00001",
    "files": [
        "a.pdf",
        "b.pdf",
        "c.pdf"
    ],
    "model_output": [{...},{...},{...},...]
}
```

## Resultado para toda uma série

Caso o resultado do modelo contemple apenas uma das séries do exame, o JSON de saída deve ser gerado preenchendo todos os campos apresentados anteriormente com os identificadores corretamente preenchidos (ids) porém deixando apenas o campo “instance_id” como nulo.

Exemplo:
```javascript
{
    "scope": "series",
    "study_id": "00000.00000.00001",
    "series_id": "00000.00001.00001",
    "files": [
        "a.pdf",
        "b.pdf",
        "c.pdf"
    ],
    "model_output": [{...},{...},{...},...]
}
```

## Resultado para uma única imagem (instância)

Caso o resultado do modelo contemple apenas uma das imagens a saída deve ser gerado preenchendo todos os campos apresentados anteriormente com os identificadores corretamente preenchidos (ids).

Exemplo:
```javascript
{
    "scope": "instance",
    "study_id": "00000.00000.00001",
    "series_id": "00000.00001.00001",
    "instance_id": "00001.00001.00001",
    "files": [
        "a.pdf",
        "b.pdf",
        "c.pdf"
    ],
    "model_output": [{...},{...},{...},...]
}
```

## Campo Model Output
O conteúdo do campo **“model_output”** deverá seguir o padrão do tipo de saída desejada. Existem 4 tipos de saídas possíveis sendo que cada uma contempla objetos de interesse diferentes dentro do exame. Mais detalhes de cada tipo podem ser vistas a seguir:

### Tipo de saída “binary”:

O tipo **“binary”** consiste em uma saída que indica valores absolutos com o uso da lógica booleana, ou seja, se existe ou não lesão, por exemplo. Essa indicação deve ser apresentada obrigatoriamente com os campos **“prediction_score”**, **binary_score”** e **“threshold”** dentro de um campo chamado **“data”**. 

```javascript
"prediction_score": float,
"binary_score": true or false,
"threshold": float
```

Exemplo:
```javascript
"model_output": [
  {
    "type": "binary",
    "label_id": "L_12382233",
    "data": {
      "prediction_score": 0.7348576,
      "binary_score": true,
      "threshold": 0.5,
      "notes": "abcdefgi"
    }
  }
]
```

### Tipo de saída “point”:
O tipo Point, representado pelo campo **“point”**, consiste em uma saída que indica um ponto de **"interesse"**. Este ponto deve ser representado como um par de coordenadas X e Y, sendo que esses valores indicam a distância em relação ao pixel de origem da imagem (0,0). Dentro de um campo chamado **“data”**. 

```javascript
"x": float,
"y": float
```
Exemplo:
```javascript
"model_output": [
  {
    "type": "point",
    "label_id": "L_12382173",
    "data": {
      "x": 45.77,
      "y": 300.89,
      "notes": "abcdef"
    }
  }
]
```

### Tipo de saída “line”:
O tipo Line, representado pelo campo **“line”**, consiste em uma saída que indica uma **"região de interesse definida por uma linha"**. Essa linha deve ser representada pelas coordenadas X e Y de início e término da linha, sendo que esses valores indicam a distância em relação ao pixel de origem da imagem (0,0). Dentro de um campo chamado **“data”**.

```javascript
"x1": float,
"y1": float,
"x2": float,
"y2": float
```
Exemplo:
```javascript
"model_output": [
  {
    "type": "line",
    "label_id": "L_12382173",
    "data": {
      "x1": 45.77,
      "y1": 300.89,
      "x2": 50.22,
      "y2": 310.23,
      "notes": "abcdef"
    }
  }
]
```

### Tipo de saída “bbox”:
O tipo Bounding Box, representado pelo campo **“bbox”**, consiste em uma saída que indica uma **"região de interesse definida por um retângulo"**. Essa região deve ser representada como um par de coordenadas X e Y, sendo que esses valores indicam a distância em relação ao pixel de origem da imagem (0,0) e pelos valores height e width. Dentro de um campo chamado **“data”**.

```javascript
"x": float,
"y": float,
"height": float,
"width": float
```

Exemplo:
```javascript
"model_output": [
  {
    "type": "bbox",
    "label_id": "L_12382173",
    "data": {
      "x": 45.77,
      "y": 300.89,
      "height": 200,
      "width": 50,
      "notes": "abcdef"
    }
  }
]
```

### Tipo de saída “polygon”:
O tipo Poligon, representado pelo campo **“polygon”**, consiste em uma saída que indica uma **"região de interesse definida por um polígono"**. Essa região deve ser representada por uma lista contendo as coordenadas dos vértices do polígono [X, Y], sendo que esses valores indicam a distância em relação ao pixel de origem da imagem (0,0). Dentro de um campo chamado **“data”**.

```javascript
"data": Objeto contendo uma lista de coordenadas X,Y
```

Exemplo:
```javascript
"model_output": [
  {
    "type": "bbox",
    "label_id": "L_12382173",
    "data": {
      "notes": "abcdef",   
      [[x1,y1], [x2,y2], ...]
    }
  }
]
```

### Tipo de saída “heatmap”:

O tipo **“heatmap”** consiste em uma saída que indica um mapa de calor caracterizando a representação de dados na forma de mapa ou diagrama, onde os dados são representados por cores. Essa região deve ser representada como uma array de valores do tipo double no campo **“data”**.

```javascript
"heatmap": Lista de valores do tipo double,
```

Exemplo:
```javascript
"model_output": [
  {
    "type": "heatmap",
    "label_id": "L_12382233",
    "data": {
      "heatmap": [
        0.4324234,
        0.234234,
        0.4234234
      ],
      "notes": "abcdef"
    }
  }
]
```

### Tipo de saída “freeform”:

O tipo **“freeform”** consiste em uma saída que indica um **“campo livre"**. Esse campo livre permite que o modelo dê como saída quaisquer campos que julgar pertinente como, por exemplo, dando uma classificação para aquele exame (lesão maligna ou benigna) ou adicionando outros comentários (“identificada possível hemorragia na região central”). Caso a saída do seu modelo não se adeque a nenhuma das outras citadas anteriormente, o tipo “freeform” deve ser empregado.

```javascript
Campos Livres
```

Exemplo:
```javascript
"model_output": [
  {
    "type": "freeform",
    "label_id": "L_12382233",
    "data": {
      "notes": "abcdef",
      "free_form": {
        "text1": "Valor",
        "text2": "Valor",
        "text3": "Valor"
      }
    }
  }
]
```

## Exemplo de uma predição válida

Toda predição passará pela validação presente no Anexo 1 deste documento.

```javascript
{
   "scope": "instance",
   "study_id": "Exemplo study",
   "series_id": "Exemplo serie",
   "instance_id": "Exemplo instance",
   "files": [
     "a.pdf",
     "b.pdf",
     "c.pdf"
   ],
   "model_output": [
     {
       "type": "binary",
       "label_id": "L_12382233",
       "data": {
         "prediction_score": 0.7348576,
         "binary_score": true,
         "threshold": 0.5,
         "notes": "abcdefgi"
       }
     },
     {
       "type": "heatmap",
       "label_id": "L_12382233",
       "data": {
         "heatmap": [
           0.4324234,
           0.234234,
           0.4234234
         ],
         "notes": "abcdef"
       }
     },
     {
       "type": "freeform",
       "label_id": "L_12382233",
       "data": {
         "free_form": {
           "text1": "Valor",
           "text2": "Valor",
           "text3": "Valor"
         },
         "notes": "abcdef"
       }
     },
     {
       "type": "bbox",
       "label_id": "L_12382173",
       "data": {
         "x": 45.77,
         "y": 300.89,
         "height": 200,
         "width": 50,
         "notes": "abcdef"
       }
     }
   ]
 }
```
> Estrutura de um output.

# 5. Requisitos para exame ser analisado

Para que um exame seja analisado pelo GASPR é necessário que ele contenha um conjunto mínimo de informações que permita identificar qual o modelo correto para fazer sua análise (se houver). Todas as informações são obtidas a partir do padrão DICOM e seguem as TAGs listadas abaixos:

## Atributos obrigatórios

- (0008, 0060): Modalidade do exame.
- (,): Parte do corpo em que o exame foi realizada. (A SER DEFINIDO)

## Atributos opcionais

- (0008, 1030): Descrição do estudo
- (0010, 0030): Data de nascimento do paciente
- (0010, 0040): Sexo do paciente
- (0010, 1010): Idade do paciente
- (0010, 1020): Altura do paciente
- (0010, 1030): Peso do paciente 
- (0028, 0010): Quantidade de linhas das imagens
- (0028, 0011): Quantidade de colunas das imagens
- (0028, 0100): Número de bits por pixel
- (0028, 2110): Se as imagens foram submetidas a uma compressão com perdas
- (0028, 0030): Espaçamento dos pixels
- (0018, 0050): Espessura das fatias
- (0008, 0022): Data de aquisição do exame

# 6. Como testar seu modelo
Para testar o algoritmo se o ambiente está funcional:
	
1. Instale e configure o Docker em sua máquina. Sugestão é seguir o documentação oficial https://docs.docker.com/get-docker/
2. Baixe o bundle disponível em https://deploy-realtime-exemplos.s3-sa-east-1.amazonaws.com/Bundle_RealTime.zip
3. Colocar seu algoritmo dentro da pasta Model
4. Colocar seu exame de teste na pasta inputs
5. Executar o comando em seu terminal: 
```sh
docker build -t teste:latest -f Dockerfile.dev . && docker run teste
```
8. Aguardar a conclusão que será impressa no terminal.

# 7. Anexos

## Anexo 1
Para cada predição oriunda dos algoritmos é executada uma validação de estrutura. O esquema abaixo demonstra a estrutura padrão de saída (output) do modelo no código JSON:

```javascript
{
  $jsonSchema: {
    bsonType: 'object',
    additionalProperties: false,
    required: [
      'scope',
      'study_id',
      'model_id',
      'end_date',
      'start_date',
      'exec_duration',
      'model_output'
    ],
    properties: {
      scope: {
        bsonType: 'string',
        'enum': [
          'study',
          'instance',
          'serie',
          'series'
        ],
        description: 'must be a string and is required'
      },
      files: {
        bsonType: 'array',
        description: 'must be a string and is required'
      },
      study_id: {
        bsonType: 'string',
        description: 'must be a string and is required'
      },
      model_id: {
        bsonType: 'objectId',
        description: 'must be a string and is required'
      },
      _id: {
        bsonType: 'objectId',
        description: 'must be a string and is required'
      },
      exec_duration: {
        bsonType: 'string',
        description: 'must be a string and is required'
      },
      series_id: {
        bsonType: 'string',
        description: 'must be a string and is required'
      },
      instance_id: {
        bsonType: 'string',
        description: 'must be a string and is required'
      },
      end_date: {
        bsonType: 'date',
        description: 'must be a date and is required'
      },
      start_date: {
        bsonType: 'date',
        description: 'must be a string and is required'
      },
      url_files: {
        bsonType: 'string',
        description: 'must be a string and is required'
      },
      model_output: {
        bsonType: [
          'array'
        ],
        minItems: 1,
        additionalProperties: false,
        items: {
          bsonType: [
            'object'
          ],
          required: [
            'label_id',
            'type',
            'data'
          ],
          additionalProperties: false,
          description: '\'items\' must contain the stated fields.',
          properties: {
            label_id: {
              description: 'must be a string and is required'
            },
            type: {
              bsonType: 'string',
              'enum': [
                'binary',
                'freeform',
                'heatmap',
                'bbox',
                'polygon',
                'line',
                'point'
              ],
              description: 'must be a string and is required'
            },
            data: {
              bsonType: [
                'object'
              ],
              minItems: 1,
              additionalProperties: true,
              items: {
                bsonType: [
                  'object'
                ],
                additionalProperties: false,
                description: '\'items\' must contain the stated fields.',
                properties: {
                  prediction_score: {
                    bsonType: 'double',
                    description: 'must be a string and is required'
                  },
                  x: {
                    bsonType: 'double',
                    description: 'must be a string and is required'
                  },
                  notes: {
                    bsonType: 'string',
                    description: 'must be a string and is required'
                  },
                  y: {
                    bsonType: 'double',
                    description: 'must be a string and is required'
                  },
                  height: {
                    bsonType: 'int',
                    description: 'must be a string and is required'
                  },
                  width: {
                    bsonType: 'int',
                    description: 'must be a string and is required'
                  },
                  threshold: {
                    bsonType: 'double',
                    description: 'must be a string and is required'
                  },
                  binary_score: {
                    bsonType: 'bool',
                    description: 'must be a string and is required'
                  },
                  free_form: {
                    bsonType: 'object',
                    description: 'must be a string and is required'
                  },
                  heatmap: {
                    bsonType: 'array',
                    description: 'must be a string and is required'
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```