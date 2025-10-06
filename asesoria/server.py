#server.py


from base import create_app
app = create_app()

#Punto de entrada principal de la aplicación Flask
#Crear la instancia de la app y la ejecuta.

if __name__ == "__main__":
    #Ejecuta la aplicación en modo debug para desarrollo.
    app.run(port=5034, debug=True)


    #En el port coloquen 5000 + el  numero de lista.


    #1. Agregar favorito
    #2. Quitar favorito
    #3. obtener favoritos
    #4. remover favorito
    #5. obtener favoritos de un usuario
    #6. obtener citas no favoritas de un usuario

