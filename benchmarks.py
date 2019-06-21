import os

def sim_cache(associatividade, tamanho_do_bloco, numero_de_blocos):
    #./sim-cache -cache:il1 il1:512:32:1:l -cache:dl1 dl1:256:16:4:l  -cache:dl2 none -cache:il2 none ~/benchmarks/mm.ss
    cache_instrucoes = "-cache:il1 il1:" + str(numero_de_blocos[0]) + ":" + str(tamanho_do_bloco[0]) + ":" + str(associatividade[0]) + ":l"
    cache_dados = "-cache:dl1 dl1:" + str(numero_de_blocos[1]) + ":" + str(tamanho_do_bloco[1]) + ":" + str(associatividade[1]) + ":l"
    benchmark_path = "../benchmark/bench_trabalho/"
    comando = "./sim-cache" + cache_instrucoes + cache_dados + "-cache:dl2 none -cache:il2 none" + benchmark_path
    resultMM = os.popen(comando + "mm.ss")
    resultMM = os.popen(comando + "amp.ss")
    resultMM = os.popen(comando + "basicmath.ss")

def trata_retorno_sim_cache():
    pass

def cacti(associatividade, tamanho_do_bloco, numero_de_blocos):
    pass

def trata_retorno_cacti():
    pass

def salva_resultados():
    pass


def main():

    # Inicia um banco de dados com os resultados
    
    associatividade= [1,1]
    tamanho_do_bloco = [4,4]
    numero_de_blocos = [32,32]
    # Roda o sim-cache nos três diferentes programas de benchmark
    sim_cache_results = sim_cache(associatividade, tamanho_do_bloco, numero_de_blocos)
    
    # Trata o retorno do sim-cache
    sim_cache_results = trata_retorno_sim_cache(sim_cache_results)
    
    # Roda o cacti com a saída do sim-cache 
    cact_results = cacti(associatividade, tamanho_do_bloco, numero_de_blocos)
    cact_results = trata_retorno_cacti(cact_results)
        # Trata o retorno do cacti
    print("FIM")

if __name__ == "__main__":
    main()