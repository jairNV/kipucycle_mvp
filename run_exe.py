import os
import sys
import streamlit.web.cli as stcli

if __name__ == '__main__':
    # Detectar si se esta ejecutando desde el .exe empaquetado o desde Python puro
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)

    app_path = os.path.join(base_path, 'app.py')
    
    # Forzar a Streamlit a ejecutarse en modo produccion limpia dentro del .exe
    sys.argv = [
        "streamlit", 
        "run", 
        app_path, 
        "--global.developmentMode=false",
        "--server.headless=true"
    ]
    sys.exit(stcli.main())