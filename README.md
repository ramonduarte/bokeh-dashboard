# bokeh-dashboard

## O que é

Uma ferramenta de visualização de gráficos interativos a partir de arquivos `.xlsx` sem utilizar diretamente código Javascript.

## Dependências

- python==2.7.8
- bokeh==0.12.6 
- pandas
- tornado>=4.4

## Como funciona?

A análise bruta dos dados é realizada pela excelente biblioteca `pandas`. Os resultados analisados são repassados a um servidor `bokeh`, que, usando a biblioteca `BokehJS`, gera gráficos interativos e visualmente impressionantes através de chamadas assíncronas próprias.

O servidor `bokeh`, baseado no `Tornado`, gera documentos HTML5 completos, com suas próprias chamadas assíncronas em JS, preparados para serem embutidos em outras páginas. 

