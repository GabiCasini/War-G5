import random


class Manager_de_Cartas:
    def __init__(self):
        self.territorios_disponiveis = ["Rio de Janeiro", "Nova Iguaçu", "Mesquita", "São João de Meriti",
                            "Seropédica", "Queimados", "Japeri", "Paracambi", "Miguel Pereira", 
                            "Eng Paulo de Frontin", "Vassouras", "Paty do Alferes", "Paraíba do Sul",
                            "Comendador Levy Gasparian", "Três Rios", "Areal", "Sapucaia", "Petrópolis",
                            "Teresópolis", "Cachoeiras de Macacu", "São José do Vale do Rio Preto",
                            "Sumidouro", "Nova Friburgo", "Bom Jardim", "Duas Barras", "Carmo", "Cantagalo",
                            "Macuco", "São Sebastião do Alto", "Itaocara", "Santo Antônio de Pádua",
                            "Cambuci", "Magé", "Guapimirim", "Itaboraí", "São Gonçalo", "Maricá", "Niterói",
                            "Cordeiro", "Trajano de Moraes", "Macaé", "Casimiro de Abreu"]
        self.territorios_em_uso = []

    def atribuir_carta(self):
        tipos = ["Círculo", "Quadrado", "Triângulo", "Coringa"]
        probabilidades = [28, 28, 28, 16]
        resultado = random.choices(tipos, weights=probabilidades, k=1)[0]

        if (resultado != "Coringa"):
            territorio = random.choice(self.territorios_disponiveis)
            self.territorios_disponiveis.remove(territorio)
            self.territorios_em_uso.append(territorio)
            
            return [resultado, territorio]
        
        return [resultado, ""]
    
    def cartas_trocadas(self, lista_de_cartas_trocadas):
        for i in lista_de_cartas_trocadas:
            if i[0] != "Coringa":
                self.territorios_em_uso.remove(i[1])
                self.territorios_disponiveis.append(i[1])

    def validar_possivel_troca(self, lista_de_cartas):
        if len(lista_de_cartas) != 3:
            return False
        
        contagem = [0, 0, 0]
        for i in lista_de_cartas:
            if i[0] == "Coringa":
                return True
            
            if i[0] == "Círculo":
                contagem[0] += 1

            elif i[0] == "Quadrado":
                contagem[1] += 1

            else:
                contagem[2] += 1
            
        if contagem[0] == contagem[1] and contagem[1] == contagem[2]:
            return True
        
        elif contagem[0] == 3 or contagem[1] == 3 or contagem[2] == 3:
            return True
        
        else:
            return False

