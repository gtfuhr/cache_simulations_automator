import subprocess as sp
import re

def sim_cache(associatividade, tamanho_do_bloco, numero_de_blocos):
    cache_instrucoes = "-cache:il1 il1:" + str(numero_de_blocos[0]) + ":" + str(tamanho_do_bloco[0]) + ":" + str(associatividade[0]) + ":l"
    cache_dados = "-cache:dl1 dl1:" + str(numero_de_blocos[1]) + ":" + str(tamanho_do_bloco[1]) + ":" + str(associatividade[1]) + ":l"
    benchmark_path = "./benchmarks/benchs_trabalho/"
    comando = "./simplesim-3.0/sim-cache " + cache_instrucoes + " " + cache_dados + " -cache:dl2 none -cache:il2 none " + benchmark_path
    # benchmarks = ["amp.ss","mm.ss","basicmath.ss"]
    benchmarks = ["mm.ss"]
    benchmark_results = [sp.getoutput(comando + benchmark) for benchmark in benchmarks]
    benchmark_treated_results = [trata_retorno_sim_cache(benchmark) for benchmark in benchmark_results]
    return benchmark_treated_results


def generate_benchmark_data(benchmark_treated_list):
    sim_cache_data = {}

    for line in benchmark_treated_list:
        infos = re.split(' +',line) # Split the line using the space as separator two times
        key, value = infos[0], float(infos[1])
        sim_cache_data[key] = value        
    
    return sim_cache_data



def trata_retorno_sim_cache(benchmark):
    # Exemplo das linhas desejadas
    
    # il1.hits                             7701959 # total number of hits		NCH 
    # il1.misses                       531 # total number of misses		NCM
    # il1.writebacks                    0 # total number of writebacks		NWB
    

    # dl1.hits                            1043160 # total number of hits		NCH
    # dl1.misses                      1387 # total number of misses		NCM
    # dl1.writebacks                  355 # total number of writebacks		NWB

    benchmark = benchmark.replace("\n",'\n')
    benchmark_list = benchmark.splitlines()
    benchmark_list_treated = []

    
    for line in benchmark_list:
        if line.count("il1.hits"):
            benchmark_list_treated.append(line)
        elif line.count("il1.misses"):
            benchmark_list_treated.append(line)
        elif line.count("il1.writebacks"):
            benchmark_list_treated.append(line)


        elif line.count("dl1.hits"):
            benchmark_list_treated.append(line)
        elif line.count("dl1.misses"):
            benchmark_list_treated.append(line)
        elif line.count("dl1.writebacks"):
            benchmark_list_treated.append(line)

    sim_cache_data = generate_benchmark_data(benchmark_list_treated)
    return sim_cache_data


def generate_cacti_data(benchmark_treated_list):
    sim_cache_data = {}

    for line in benchmark_treated_list:
        infos = re.split(' +',line) # Split the line using the space as separator two times
        if(line.count("Cache height x width (mm):") == 0):
            key, value = infos[1], float(infos[4])
        else:
            key, value = infos[1], (float(infos[8]), float(infos[6]))
        sim_cache_data[key] = value        
    
    return sim_cache_data

def a(x):
    print(x)
    exit(0)

def trata_retorno_cacti(cacti):
    # Exemplo das linhas desejadas

    # Access time (ns): 1.24238		LAC
    # Read Energy (nJ): 0.0361295		EAC
    # Cache height x width (mm): 0.23248 x 0.122094
    cacti = cacti.replace("\n",'\n')
    cacti_list = cacti.splitlines()
    cacti_list_treated = []

    
    for line in cacti_list:
        if line.count("Access time (ns):"):
            cacti_list_treated.append(line)
        elif line.count("Read Energy (nJ):"):
            cacti_list_treated.append(line)
        elif line.count("Cache height x width (mm):"):
            cacti_list_treated.append(line)

    cacti_data = generate_cacti_data(cacti_list_treated)
    return cacti_data

def cacti(associatividade, tamanho_do_bloco, numero_de_blocos, cache_num):
    comando = "./cacti65/cacti -infile cache.cfg"
    cacti_all_results = []
    for i in range(cache_num):
        tamanho_total = tamanho_do_bloco[i] * numero_de_blocos[i]

        cache_cfg = """
        # Cache size
        -size (bytes) {tamanho_tot}

        # Line size
        -block size (bytes) {bloco_tamanho}

        # To model Fully Associative cache, set associativity to zero

        -associativity {associativi}
        """.format(tamanho_tot = tamanho_total, bloco_tamanho = tamanho_do_bloco[i], associativi = associatividade[i])

        cache_cfg_rest = open("./cacti65/cache_rest.cfg","r").readlines()
        cache_cfg = cache_cfg + str(cache_cfg_rest).replace("\n",'\n')
        open("./cacti65/cache.cfg",'w').write(cache_cfg)

        cacti_results = sp.getoutput(comando)
        cacti_all_results.append(cacti_results)
    
    cacti_treated_results = [trata_retorno_cacti(cacti) for cacti in cacti_all_results]
    return cacti_treated_results


def testa_cache(associatividade,tamanho_do_bloco,numero_de_blocos):
    """
        Recebe três listas contendo a associatividade, tamanho dos blocos e os numeros de blocos da 
        cache de instruções e da cache de dados 
    """
    # Roda o sim-cache nos três diferentes programas de benchmark
    sim_cache_results = sim_cache(associatividade, tamanho_do_bloco, numero_de_blocos)
    
    # Roda o cacti com a saída do sim-cache 
    cact_results = cacti(associatividade, tamanho_do_bloco, numero_de_blocos,len(associatividade))
    
    return sim_cache_results, cact_results

def energia_cache(sim_cache_data,cacti_data):
    # RAM INFO to be used
    # Cycle time (ns):  13.6692
    # Read Energy (nJ): 8.64848
    LAMP = 13.6692
    EAMP = 8.64848

    # Constantes - Tipo de memória
    INST = 0
    DADOS = 1

    energia_total_INST = energia_total_DADOS = 0
    # Energia total da memoria de instruções:
    for sim_cache_test in sim_cache_data:
           NCH = sim_cache_test.get('il1.hits')
           EAC = cacti_data[INST].get('Read')
           NCM = sim_cache_test.get('il1.misses')
           NWB = sim_cache_test.get('il1.writebacks')
           energia_total_INST += NCH*EAC + NCM*EAC +NCM*EAMP + NWB*EAMP
    # energia_total_ = NCH*EAC + NCM*EAC +NCM*EAMP + NWB*EAMP 

    # Energia total da memoria de dados:
    for sim_cache_test in sim_cache_data:
           NCH = sim_cache_test.get('dl1.hits')
           EAC = cacti_data[DADOS].get('Read')
           NCM = sim_cache_test.get('dl1.misses')
           NWB = sim_cache_test.get('dl1.writebacks')
           energia_total_DADOS += NCH*EAC + NCM*EAC +NCM*EAMP + NWB*EAMP
    # energia_total_DADOS = NCH*EAC + NCM*EAC +NCM*EAMP + NWB*EAMP 
    # (onde EAMP é Energia de um Acesso à Mem. Principal)
    return energia_total_INST, energia_total_DADOS

def tempo_cache(sim_cache_data,cacti_data):
    # RAM INFO to be used
    # Cycle time (ns):  13.6692
    # Read Energy (nJ): 8.64848
    LAMP = 13.6692
    EAMP = 8.64848

    # Constantes - Tipo de memória cache
    INST = 0
    DADOS = 1

    tempo_total_INST = tempo_total_DADOS = 0

    # Tempo total da memoria de instruções:
    for sim_cache_test in sim_cache_data:
        NCH = sim_cache_test.get('il1.hits')
        LAC = cacti_data[INST].get('Access')
        NCM = sim_cache_test.get('il1.misses')
        NWB = sim_cache_test.get('il1.writebacks')
        tempo_total_INST += NCH*LAC + NCM*LAC +NCM*LAMP + NWB*LAMP 

    # Tempo total da memoria de dados:
    for sim_cache_test in sim_cache_data:
       NCH = sim_cache_test.get('dl1.hits')
       LAC = cacti_data[DADOS].get('Access')
       NCM = sim_cache_test.get('dl1.misses')
       NWB = sim_cache_test.get('dl1.writebacks')
       tempo_total_DADOS += NCH*LAC + NCM*LAC +NCM*LAMP + NWB*LAMP
    # tempo_total_DADOS = NCH*LAC + NCM*LAC +NCM*LAMP + NWB*LAMP 
    # (onde LAMP é Latência de um Acesso à Mem. Principal, NWB é o Número de writebacks)
    return tempo_total_INST,tempo_total_DADOS

def metricas_cache(associatividade, tamanho_do_bloco, numero_de_blocos):
    sim_cache_data, cacti_data = testa_cache(associatividade,tamanho_do_bloco,numero_de_blocos)

    tempo_total_INST, tempo_total_DADOS = tempo_cache(sim_cache_data,cacti_data)
    energia_total_INST, energia_total_DADOS = energia_cache(sim_cache_data,cacti_data)
    
    # Constantes - Tipo de memória cache
    INST = 0
    DADOS = 1

    print("Tempo total","Energia total")
    print("INST","A =",associatividade[INST],"TB =",tamanho_do_bloco[INST],"NB =",numero_de_blocos[INST])
    print(tempo_total_INST,energia_total_INST)
    print("DADOS","A =",associatividade[DADOS],"TB =",tamanho_do_bloco[DADOS],"NB =",numero_de_blocos[DADOS])
    print(tempo_total_DADOS,energia_total_DADOS)
    print()
    return tempo_total_INST, tempo_total_DADOS, energia_total_INST, energia_total_DADOS

def salva_resultados(tempo_I, tempo_D, energia_I, energia_D, associatividade, tamanho_do_bloco, numero_de_blocos):
    # Inicia um banco de dados com os resultados
    # To be done
    pass

def menu():
    qual_varia = input(
        """Escolha qual das caracteristicas da memoria cache irá variar:
        [1] Associatividade
        [2] Numero de Blocos
        [3] Tamanho do Bloco
        Insira um número para escolher:
        """)
    if(qual_varia == '1'):
        qual_varia = "Associatividade"
    elif(qual_varia == '2'):
        qual_varia = "Numero de Blocos"
    elif(qual_varia == '3'):
        qual_varia = "Tamanho do Bloco"
    else:
        print("Digite uma opcao valida!")
        exit(0)
    if(qual_varia == "Tamanho do Bloco"):
        quanto_varia = str(input(
            """Determine qual o intervalo das potências de 2 de variação para {qual_var}:
            Exemplo: 3,5 (O valor minimo para o tamanho de bloco é 8, 
            logo, o valor inicial é fixo em três)
            Saida: 8,16,32
            Insira um intervalo: (X >= 3) Ex: X,Y:
            """.format(qual_var = qual_varia)))
    else:
        quanto_varia = str(input(
            """Determine qual o intervalo das potências de 2 de variação para {qual_var}:
            Exemplo: 0,3
            Saida: 1,2,4,8
            Insira um intervalo. Ex: X,Y:
            """.format(qual_var = qual_varia)))
    
    quanto_varia = [int(x) for x in quanto_varia.split(',')]
    if(len(quanto_varia) != 2):
        print("Digite um range valido!")
        exit(0)
    return qual_varia, quanto_varia    

def main():
    associatividade = [2,2] 
    tamanho_do_bloco = [8,8] 
    numero_de_blocos = [32,32]
    qual_varia, quanto_varia = menu()
    
    for i in range(quanto_varia[1]):
        for j in range(quanto_varia[1]):
            if(qual_varia == "Associatividade"):
                associatividade = [
                    2**i, # Associatividade memória cache de Instruções
                    2**j  # Associatividade memória cache de Dados
                ]
            elif(qual_varia == "Tamanho do Bloco"):
                tamanho_do_bloco = [
                    2**(i+3), # Tamanho do bloco da memória cache Instruções
                    2**(j+3)  # Tamanho do bloco da memória cache Dados
                ]
            elif(qual_varia == "Numero de Blocos"):
                numero_de_blocos = [
                    2**i, # Numero de blocos da memória cache Instruções
                    2**j  # Numero de blocos da memória cache Dados
                ]
            tempo_I, tempo_D, energia_I, energia_D = metricas_cache(associatividade,tamanho_do_bloco,numero_de_blocos)
            salva_resultados(tempo_I, tempo_D, energia_I, energia_D, associatividade, tamanho_do_bloco, numero_de_blocos)

    print("FIM")

if __name__ == "__main__":
    main()