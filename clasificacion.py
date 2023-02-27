# Clase que se utilizará para crear los datos de entrenamiento y los datos de prueba.
class Data:
    def __init__(self, driving_type, mean, std_deviation, variance):
        self.driving_type = driving_type
        self.mean = mean
        self.std_deviation = std_deviation
        self.variance = variance


# Funciones para añadir un formato a los resultados mostrados.
def print_table(list):
    print("+-------------------------------------------------------+")
    print("|Conducción|    Media     |Desv. estándar|   Varianza   |")
    print("+-------------------------------------------------------+")
    for element in list:
        driving_type = element.driving_type
        if driving_type.find("_") > -1:
            driving_type = driving_type.split("_")
            acronym = ""
            for word in driving_type:
                acronym = acronym + word[0:1]
            driving_type = "  " + acronym.upper() + "   "
        value = "{:.10f}"
        print("| " + driving_type + " ", end="|")
        print(" " + value.format(element.mean) + " ", end="|")
        print(" " + value.format(element.std_deviation) + " ", end="|")
        print(" " + value.format(element.variance) + " |")
    print("+-------------------------------------------------------+\n")

def format_content(content, reference):
        while len(content) < len(reference):
            if len(content) == len(reference) -1:
                content = content + "|"
                break
            content = content + " "
        return content

def format_text(text):
        text = text.capitalize()
        text = text.replace("_", " ")
        text = text.replace("rapida", "rápida")
        return text


# Importación de módulos para crear una conexión a una base de datos, 
# trabajar con arreglos y utilizar funciones estadísticas como: 
# media "numpy.mean()", desviación estándar "numpy.std()" y varianza "numpy.var()".
import mysql.connector
import numpy

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="dataset_conduccion_vehicular"
)
cursor = db.cursor()


# Creación de los datos de entrenamiento.
cursor.execute("SHOW TABLES")
table_names = []
training_data = []

for table in cursor:
    table_name = str(table)
    table_names.append(table_name.strip("()',"))

for table_name in table_names:
    cursor.execute("SELECT `suma_vectorial` FROM `" + table_name + "` WHERE id BETWEEN 1 AND 6000")
    values = numpy.array(cursor.fetchall())
    training_data.append(
        Data(
            table_name, 
            numpy.mean(values), 
            numpy.std(values), 
            numpy.var(values)
        )
    )

print("\nDatos de entrenamiento:")
print_table(training_data)


# Mostrar las bases de datos que existen.
database_list = []
print("Listado de bases de datos:")
cursor.execute("SHOW DATABASES")

for database in cursor:
    print(database)
    database_name = str(database)
    database_list.append(database_name.strip("()',"))

print()


# El usuario seleccionará la base de datos de la cual se extraerán las pruebas.
x = True

while x:
    selected_database = input("Escriba el nombre de la base de datos para las pruebas: ")
    selected_database = selected_database.strip()
    selected_database = selected_database.strip("()',")

    for existing_database in database_list:
        if selected_database == existing_database:
            x = False
            db.database = selected_database
            break

print("\nBase de datos seleccionada:", selected_database)


# Creación de los datos de prueba
cursor.execute("SHOW TABLES")
table_names = []
testing_data = []
test_number = 1

for table in cursor:
    table_name = str(table)
    table_names.append(table_name.strip("()',"))

for table_name in table_names:
    query = "SELECT `suma_vectorial` FROM `" + table_name + "`"

    if selected_database == "dataset_conduccion_vehicular":
        query = query + " WHERE id BETWEEN 6001 AND 9000"
    
    cursor.execute(query)
    values = numpy.array(cursor.fetchall())
    testing_data.append(
        Data(
            "Prueba " + str(test_number),
            numpy.mean(values), 
            numpy.std(values), 
            numpy.var(values)
        )
    )
    test_number += 1

print("\nDatos de prueba:")
print_table(testing_data)


# Clasificación de las pruebas en base a los datos de entrenamiento. 
test_number = 1
for test in testing_data:
    test.driving_type = []

    # Comparar la diferencia entre los valores de la prueba y los valores de cada uno
    # de los datos de entrenamiento.
    diff_between_means = []
    diff_between_std_deviations = []
    diff_between_variances = []

    for element in training_data:
        diff_between_means.append(abs(element.mean - test.mean))
        diff_between_std_deviations.append(abs(element.std_deviation - test.std_deviation))
        diff_between_variances.append(abs(element.variance - test.variance))
    
    
    # La diferencia más pequeña de valores (media, desviación estándar y varianza)
    # representa el tipo de conducción al que se aproxima más la prueba.
    min_diff_between_means = min(diff_between_means)
    min_diff_between_std_deviations = min(diff_between_std_deviations)
    min_diff_between_variances = min(diff_between_variances)

    for i in range(len(training_data)):
        if min_diff_between_means == diff_between_means[i]:
            test.driving_type.append(training_data[i].driving_type)
            break
    
    for i in range(len(training_data)):
        if min_diff_between_std_deviations == diff_between_std_deviations[i]:
            test.driving_type.append(training_data[i].driving_type)
            break
    
    for i in range(len(training_data)):
        if min_diff_between_variances == diff_between_variances[i]:
            test.driving_type.append(training_data[i].driving_type)
            break
    

    # Revisión de las respuestas del tipo de conducción de la prueba.
    driving_types = test.driving_type
    results = {}
    for driving_type in driving_types:
        total_matches = driving_types.count(driving_type)
        results[driving_type] = total_matches
    

    # El tipo de conducción repetido más veces es el resultado.
    maximum = max(results.values())
    for key, value in results.items():
        if value == maximum:
            test.driving_type = key
            break
    

    # Mostrar resultados del tipo de conducción de la prueba.
    dividing_line = "+----------------------------------------------------------+"
    print(dividing_line)

    print("|   Determinación del tipo de conducción de la prueba", test_number, "   |")
    print(dividing_line)

    content = "|En base a la media: " + format_text(driving_types[0])
    print(format_content(content, dividing_line))

    content = "|En base a la desviación estándar: " + format_text(driving_types[1])
    print(format_content(content, dividing_line))

    content = "|En base a la varianza: " + format_text(driving_types[2])
    print(format_content(content, dividing_line))

    content = "|Resultado final: " + format_text(test.driving_type)
    print(format_content(content, dividing_line))
    print(dividing_line + "\n")

    test_number += 1
