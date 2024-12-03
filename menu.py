def mostrar_menu():
    while True:
        print("\nMenú Principal")
        print("1. Actualización de datos")
        print("2. Visualización de datos")
        print("3. Salir")


        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print("Ud. presionó la opción 1: Actualización de datos")
        elif opcion == "2":
            print("Ud. presionó la opción 2: Visualización de datos")
        elif opcion == "3":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente de nuevo.")

mostrar_menu()