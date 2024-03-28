# Compilador

Este repositorio contiene el Código fuente del frontend de un compilador para una gramática basada en Chocolatey, la gramática se encuentra específicada con mayor detalle en test/grammar.txt.
El frontend se encarga de las tareas de análisis léxico y sintáctico, así como de la generación del árbol de sintaxis.

## Estructura de archivos

El repositorio está organizado de la siguiente manera:

- **files**: Carpeta que contiene archivos de prueba para el compilador.
- **test**: Carpeta que contiene scripts de prueba y archivos de gramática.
- **utils**: Carpeta que contiene utilidades y clases auxiliares para el compilador.

Archivos principales:

- **Compiler.py**: Archivo principal del compilador que orquesta el análisis léxico y sintáctico.
- **Parser.py**: Implementación del analizador sintáctico (parser).
- **Scanner.py**: Implementación del analizador léxico (scanner).
- **genDerivations.py**: Script para generar producciones de prueba para probar el parse y el escaner
- **treeTest.py**: OUTDATED Script de prueba para verificar la generación del árbol de sintaxis.

## Elaborado por
María Cruz Cáceres: maria.cruz@ucsp.edu.pe
