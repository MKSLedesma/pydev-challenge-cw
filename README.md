# pydev-challenge-cw
Prueba técnica para puesto Python Developer Jr. 

# Iteración 1: Scraper Base
Implementación inicial del pipeline asíncrono para extraccion de metricas de laboratorios farmaceuticos desde Stock Analysis.
Se establece el cliente HTTP asincrono, el control de concurrencia y deteccion del árbol DOM de las estadísticas.

# Iteración 2: Funciones auxiliares de parseo 
Normalización de Magnitudes y Tratamiento de Valores Ausentes
* Escala de Magnitudes Financieras:
    Stock Analysis compacta cifras en tablas usando:
    * `M`: factor de 10**6
    * `B`: factor de 10**9
    * `T`: factor de 10**12

    Todas las cifras con simbolos monetarios (`$`) y abreviación de escala se normalizan a un `float` en su unidad base monetaria (USD).
    <div align="center">
        <img src="docs/t_sufix.png" width="400">
        <img src="docs/b_sufix.png" width="400">
        <img src="docs/m_sufix.png" width="400">
    </div>

* Diferenciación de Nulos vs. Ceros:
    La pagina presenta valores faltantes bajo dos representaciones principales detectadas en las tablas: guión simple (`"-"`) y el string `"n/a"`.
    * Dato no existente: Las cadenas `"-"`, `"n/a"` y vacios se normalizan a `None` en Python y se persistiran como NULL en SQL.
    <div align="center">
        <img src="docs/dash_example.png" width="400">
        <img src="docs/na_example.png" width="400">
    </div>
    
    * Valor cero: Un valor explicito en cero se preserva numericamente como `0.0`. 
    
## Criterio de Selección de Compañías
* Fuente: Sector Drug Manufacturers - General en Stock Analysis 
    `https://stockanalysis.com/stocks/industry/drug-manufacturers-general/`

* Fecha de consulta: 17 de septiembre de 2026

* Criterio aplicado: Selección de los 10 laboratorios farmacéuticos cotizados con mayor capitalización bursátil (`Market Cap`) listados directamente con ticker de EE. UU. (NYSE):
    * `LLY`, `JNJ`, `ABBV`, `MRK`, `NVS`, `AZN`, `AMGN`, `NVO`, `GILD`, `PFE`

## Brechas de Cobertura
* Filtro de mercado: Se consideraron unicamente compañias listadas en la bolsa de Nueva York. Laboratorios internacionales no se incluyeron en esta iteración para mantener un formato de URL y moneda homogéneo dentro de Stock Analysis.

## Decisiones de Diseño y Asunciones Técnicas
* Control de Concurrencia: Se implementó `asyncio.Semaphore(2)` a nivel de scraper para garantizar que no existan más de 2 peticiones HTTP activas de manera simultánea.

* Aislamiento de Errores por Ticker: Cada petición se resuelve dentro de un bloque try/except, de modo que el fallo o timeout en un laboratorio no interrumpa la ejecución de las faltantes.

* Alcance: Esta iteración cubre la conexion a Stock Analyst y la localizacion de los elementos `<table>` con BeautifulSoup. El parseo de métricas individuales, normalización y almacenamiento quedan delegados a los módulos `parser.py` y `database.py` en los posteriores commits.

## Uso de Inteligencia Artificial 
* Herramienta: Gemini como Asistente de IA
* Alcance: Asistencia en el diseño estructural del repositorio y revisión del borrador del README.