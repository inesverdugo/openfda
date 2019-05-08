import http.server
import http.client
import json
import socketserver
#De la openfda nos va a llegar información de ficheros json 

IP = "localhost" 
PORT = 8000
#Conjunto de recursos que vamos a utilizar de la FDA

servidor_rest = "api.fda.gov"
openfda_event = "/drug/label.json"
fda_componente  = "&search=active_ingredient:"
fda_laboratorio ='&search=openfda.manufacturer_name:'

MAX_OPEN_REQUESTS = 5

class OpenFDAParser():
#Lógica para obtener los datos de los medicamentos

    def paginainicio(self): #Funcion para abrir el documento que contiene el html del formulario
        filename = "formulario.html"
        with open(filename) as f:
            content = f.read()
        print("File to send: {}".format(filename))
        return content

    def openfda_req(self, limit=10):
        conn =http.client.HTTPSConnection(servidor_rest)
        conn.request("GET", "/drug/label.json" + "?limit="+str(limit))
        print ("/drug/label.json"+ "?limit="+str(limit))
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        drugs_json = r1.read().decode("utf-8")
        data = json.loads(drugs_json)
        mensaje = data["results"] # "results": contiene los resultados de la busqueda
        return mensaje

    def resultados_busquedamedi(self, limit = "10"):
        drug = self.path.split('=')[1]
        connection = http.client.HTTPSConnection("api.fda.gov")
        connection.request('GET', '/drug/label.json' + '?limit=' + str(limit) + '&search=active_ingredient:' + drug)
        respuesta = connection.getresponse()
        leer = respuesta.read().decode('utf8')
        dato = json.loads(leer)
        return dato

    def resultados_busquedaempresas(self, limit = "10"):
        compania = self.path.split('=')[1]
        connection = http.client.HTTPSConnection("api.fda.gov")
        connection.request('GET', '/drug/label.json' + '?limit=' + str(limit) + "&search=openfda.manufacturer_name:" + compania)
        respuesta = connection.getresponse()
        leer = respuesta.read().decode('utf8')
        dato = json.loads(leer)
        return dato


class OpenFDAHTML(OpenFDAParser):

#Función para que te de la pag web
    def html_web (self, lista):
        list_html = """
                                <html>
                                    <head>
                                        <title>OpenFDA Cool App</title>
            <h3> <a href='/'>Volver</a> 
                                    </head>
                                    <body>
                                        <ul>
                            """
        for item in lista:
            list_html += "<li>" + item + "</li>"

        list_html += """
                                        </ul>
                                    </body>
                                </html>
                            """
        return list_html



#html para que de errores

    def htmlerrores(self):
        errores = '''
        <html>
            <head>
            <meta charset="utf-8">
            <title> Error </title>

            <body>
            <h3> <a href='/'>Volver</a> Se ha detectado un error: </h3>
            <h5> No se ha encontrado información sobre el valor introducido. </h5>
            </body>
            </html>'''

        return errores

class testHTTPRequestHandler(http.server.BaseHTTPRequestHandler, OpenFDAHTML):

    def do_GET(self):
#Obtenemos los parametros
        recurso_lista = self.path.split('?')
        if len(recurso_lista) > 1:
            parametro = recurso_lista[1]
        else:
            parametro = ''
        limit = 1
        if parametro:
            analizar_limite = parametro.split('=')
            try:
                if analizar_limite[0] == 'limit':
                    limit = int(analizar_limite[1])
                    
            except ValueError:
                limit = 1
      


        if self.path == "/" or self.path == "/index" or self.path == " ":
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = self.paginainicio()
            self.wfile.write(bytes(message, "utf8"))
            

        elif  "/listDrugs" in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            print("Lista de medicamentos")
            resultados = self.openfda_req(limit)
            medicamentos_list = []
            for resultado in resultados:
                # Nombre del componente principal:
                if ('generic_name' in resultado['openfda']) == True:
                    medicamentos_list.append(resultado['openfda']['generic_name'][0])
                else:
                    medicamentos_list.append('No se conoce.')
            message = self.html_web(medicamentos_list)
            self.wfile.write(bytes(message, "utf8"))

        elif "/listCompanies" in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            drugs = self.openfda_req(limit)
            empresas_list = []
            for drug in drugs:
                if ('manufacturer_name' in drug['openfda']) == True:
                    empresas_list.append(drug['openfda']['manufacturer_name'][0])
                else:
                    empresas_list.append('No se conoce.')
            message = self.html_web(empresas_list)
            self.wfile.write(bytes(message, "utf8"))

        elif "/listWarnings" in self.path :
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            warnings = []
            resultados = self.openfda_req (limit)
            for resultado in resultados:
                if ('warnings' in resultado):
                    warnings.append (resultado['warnings'][0])
                else:
                    warnings.append('Desconocido')
            resultado_html = self.html_web(warnings)
            self.wfile.write(bytes(resultado_html, "utf8"))

        elif "/searchDrug" in self.path:
           
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            resultado1 = self.resultados_busquedamedi()
            medicinas = []
            try:
                resultados = resultado1["results"]
                for resultado in resultados:
                    if ('substance_name' in resultado['openfda']):
                        medicinas.append(resultado['openfda']['generic_name'][0])
                    else:
                        medicinas.append('Desconocido')
                message = self.html_web(medicinas)
                self.wfile.write(bytes(message, "utf8"))
            except KeyError:
                errores = self.htmlerrores()
                self.wfile.write(bytes(errores, 'utf8'))
       
        elif "/searchCompany" in self.path:

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            listaempresas = []
            resultados1 = self.resultados_busquedaempresas()
            try:
                resultados = resultados1["results"]
                for resultado in resultados:
                    if ('manufacturer_name' in resultado['openfda']):
                        listaempresas.append(resultado['openfda']['generic_name'][0])
                    else:
                        listaempresas.append('Desconocido')
                message = self.html_web(listaempresas)
                self.wfile.write(bytes(message, "utf8"))
            except KeyError:
                errores = self.htmlerrores()
                self.wfile.write(bytes(errores, 'utf8'))

        elif  "/secret" in self.path:
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Basic realm="Mi servidor"')
            self.end_headers()


        elif 'redirect' in self.path:
            print('Mandamos la redireccion a la página principal')
            self.send_response(301)
            self.send_header('Location', 'http://localhost:'+str(PORT))
            self.end_headers()

        else: 
            self.send_error(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("No se encuentra el archivo '{}'.".format(self.path).encode())
        return


class OpenFDAClient():
#Incluye la lógica para comunicarse con la API de OpenFDA
    socketserver.TCPServer.allow_reuse_address= True
# Handler: manejador, es una instancia de la clase, sabe responder ante un do get, manejador de http.
    Handler = testHTTPRequestHandler
    httpd = socketserver.TCPServer(("", PORT), Handler)
    print("serving at port", PORT)
