PYTHON VERSION 3.8

SIN DOCKER

Instalar dependencias
* `pip install -r requirements.txt`

Levantar aplicacion
* `python app.py`

CON DOCKER

* `docker-compose up`

Configuracion -> para probarlo local se debera:

* Crear un bot propio en telegram. 
* Cambiar en app.py el valor de TOKEN por el del nuevo bot.
* Cambiar en app.py el valor de DEV_CHAT_ID por el chat_id propio.


ACLARACION: Para esta entrega v0.1, faltan algunos features para usuario admin y faltaria setear el webhook a un servidor que se levante con ngrok (que por cierto es dinamico)