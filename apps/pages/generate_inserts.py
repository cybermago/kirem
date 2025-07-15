import random
from decimal import Decimal

def generate_realistic_device_catalog_inserts(num_entries_per_device_type=5):
    """
    Gera comandos INSERT com dados mais realistas para a tabela device_catalog,
    baseados em tipos de dispositivos específicos e marcas.

    Args:
        num_entries_per_device_type (int): Número de entradas a serem geradas
                                           para cada tipo de dispositivo predefinido.

    Returns:
        list: Uma lista de strings, onde cada string é um comando INSERT SQL.
    """

    # Dados mais realistas e predefinidos para dispositivos
    # Cada entrada contém (name, icon_base, avg_kwh, procel_seal, categoria, potencia_nominal, tensao, marca)
    realistic_devices_data = {
        # Eletrodomésticos de linha branca
        "Geladeira": [
            ("Geladeira Frost Free 400L", "geladeira_400l.png", Decimal("45.00"), "A", "ELETRODOMESTICO", "100", "220", "BRASTEMP"),
            ("Geladeira Side by Side", "geladeira_side.png", Decimal("55.00"), "A", "ELETRODOMESTICO", "150", "127", "LG"),
            ("Geladeira Inverse 450L", "geladeira_inverse.png", Decimal("48.00"), "A", "ELETRODOMESTICO", "120", "BIVOLT", "CONSUL"),
            ("Geladeira Duplex 350L", "geladeira_duplex.png", Decimal("40.00"), "A", "ELETRODOMESTICO", "90", "220", "ELETROLUX"),
            ("Geladeira Smart Inverter", "geladeira_smart.png", Decimal("42.00"), "A", "ELETRODOMESTICO", "110", "127", "SAMSUNG"),
            
        ],
        "Freezer": [
            ("Freezer Vertical 200L", "freezer_vertical.png", Decimal("35.00"), "A", "ELETRODOMESTICO", "80", "127", "CONSUL"),
            ("Freezer Horizontal 300L", "freezer_horizontal.png", Decimal("40.00"), "A", "ELETRODOMESTICO", "100", "220", "BRASTEMP"),
        ],
        "Fogão elétrico": [
            ("Fogão 4 Bocas Vitrocerâmico", "fogao_vitro.png", Decimal("10.00"), "NA", "ELETRODOMESTICO", "4000", "220", "ELETROLUX"),
            ("Fogão de Indução 2 Zonas", "fogao_inducao.png", Decimal("8.00"), "NA", "ELETRODOMESTICO", "3500", "220", "PHILIPS"),
        ],
        "Forno elétrico": [
            ("Forno Elétrico Embutir 60L", "forno_embutir.png", Decimal("7.00"), "NA", "ELETRODOMESTICO", "2500", "220", "BRASTEMP"),
            ("Forno Elétrico Bancada 45L", "forno_bancada.png", Decimal("5.00"), "NA", "ELETRODOMESTICO", "2000", "127", "MIDEA"),
        ],
        "Micro-ondas": [
            ("Micro-ondas 20L", "microondas_20l.png", Decimal("1.50"), "A", "ELETRODOMESTICO", "1100", "127", "LG"),
            ("Micro-ondas 30L Grill", "microondas_30l.png", Decimal("2.00"), "A", "ELETRODOMESTICO", "1400", "220", "SAMSUNG"),
        ],
        "Lava-louças": [
            ("Lava-louças 8 Serviços", "lava_loucas_8s.png", Decimal("1.00"), "A", "ELETRODOMESTICO", "1500", "220", "BRASTEMP"),
            ("Lava-louças 12 Serviços", "lava_loucas_12s.png", Decimal("1.20"), "A", "ELETRODOMESTICO", "1800", "127", "ELETROLUX"),
        ],
        "Máquina de lavar roupas": [
            ("Máquina Lavar 12kg", "lavadora_12kg.png", Decimal("0.30"), "A", "ELETRODOMESTICO", "500", "127", "CONSUL"),
            ("Máquina Lavar Frontal 10kg", "lavadora_frontal.png", Decimal("0.25"), "A", "ELETRODOMESTICO", "450", "220", "LG"),
        ],
        "Secadora de roupas": [
            ("Secadora de Roupas 10kg", "secadora_10kg.png", Decimal("3.00"), "B", "ELETRODOMESTICO", "2000", "220", "ELETROLUX"),
        ],
        "Tanquinho": [
            ("Tanquinho Semiautomático 8kg", "tanquinho_8kg.png", Decimal("0.10"), "NA", "ELETRODOMESTICO", "250", "127", "MIDEA"),
        ],
        "Depurador de ar / Coifa": [
            ("Depurador de Ar 60cm", "depurador_60cm.png", Decimal("0.05"), "NA", "ELETRODOMESTICO", "150", "127", "CONSUL"),
            ("Coifa de Parede 90cm", "coifa_90cm.png", Decimal("0.15"), "NA", "ELETRODOMESTICO", "300", "220", "BRASTEMP"),
        ],
        # Pequenos eletrodomésticos de cozinha
        "Liquidificador": [
            ("Liquidificador Power 700W", "liquidificador_700w.png", Decimal("0.02"), "NA", "ELETRONICOS", "700", "BIVOLT", "PHILIPS"),
            ("Liquidificador Portátil USB", "liquidificador_usb.png", Decimal("0.01"), "NA", "ELETRONICOS", "60", "BIVOLT", "OUTRA"),
        ],
        "Batedeira": [
            ("Batedeira Planetária", "batedeira_planetaria.png", Decimal("0.03"), "NA", "ELETRONICOS", "350", "127", "ARNO"),
        ],
        "Sanduicheira / Grill": [
            ("Sanduicheira e Grill", "sanduicheira_grill.png", Decimal("0.04"), "NA", "ELETRONICOS", "750", "BIVOLT", "MONDIAL"),
        ],
        "Torradeira": [
            ("Torradeira Elétrica 2 Fatias", "torradeira_2fatias.png", Decimal("0.02"), "NA", "ELETRONICOS", "800", "127", "PHILIPS"),
        ],
        "Cafeteira elétrica": [
            ("Cafeteira Elétrica 30 Xícaras", "cafeteira_30xic.png", Decimal("0.03"), "NA", "ELETRONICOS", "1000", "127", "ARNO"),
            ("Máquina de Café Expresso", "maquina_expresso.png", Decimal("0.05"), "NA", "ELETRONICOS", "1300", "220", "NESPRESSO"),
        ],
        "Panela elétrica": [
            ("Panela de Pressão Elétrica 5L", "panela_pressao_eletrica.png", Decimal("0.06"), "NA", "ELETRONICOS", "900", "127", "PHILIPS"),
        ],
        "Fritadeira elétrica (air fryer)": [
            ("Air Fryer 4L", "airfryer_4l.png", Decimal("0.08"), "NA", "ELETRONICOS", "1500", "127", "MONDIAL"),
            ("Air Fryer Digital 5L", "airfryer_5l.png", Decimal("0.09"), "NA", "ELETRONICOS", "1800", "220", "PHILIPS"),
        ],
        "Espremedor de frutas": [
            ("Espremedor de Frutas Elétrico", "espremedor_eletrico.png", Decimal("0.01"), "NA", "ELETRONICOS", "200", "BIVOLT", "MONDIAL"),
        ],
        "Processador de alimentos": [
            ("Processador de Alimentos Completo", "processador_completo.png", Decimal("0.04"), "NA", "ELETRONICOS", "700", "127", "PHILIPS"),
        ],
        "Chaleira elétrica": [
            ("Chaleira Elétrica 1.7L", "chaleira_eletrica.png", Decimal("0.03"), "NA", "ELETRONICOS", "1500", "127", "CADENCE"),
        ],
        # Climatização e conforto
        "Ar-condicionado": [
            ("Ar-condicionado Split Inverter 9000 BTU/h", "ac_split_9000.png", Decimal("15.00"), "A", "CLIMATIZACAO", "850", "220", "LG"),
            ("Ar-condicionado Janela 7500 BTU/h", "ac_janela_7500.png", Decimal("18.00"), "B", "CLIMATIZACAO", "700", "220", "CONSUL"),
            ("Ar-condicionado Portátil 12000 BTU/h", "ac_portatil_12000.png", Decimal("20.00"), "C", "CLIMATIZACAO", "1100", "127", "MIDEA"),
        ],
        "Ventilador": [
            ("Ventilador de Coluna 40cm", "ventilador_coluna.png", Decimal("0.07"), "NA", "CLIMATIZACAO", "60", "BIVOLT", "MONDIAL"),
            ("Ventilador de Teto com Controle", "ventilador_teto.png", Decimal("0.09"), "NA", "CLIMATIZACAO", "100", "220", "ARNO"),
        ],
        "Aquecedor elétrico": [
            ("Aquecedor Elétrico Halógeno", "aquecedor_halogeno.png", Decimal("0.10"), "NA", "AQUECIMENTO", "1500", "127", "MONDIAL"),
            ("Aquecedor a Óleo 1500W", "aquecedor_oleo.png", Decimal("0.12"), "NA", "AQUECIMENTO", "1500", "220", "OUTRA"),
        ],
        "Umidificador": [
            ("Umidificador de Ar Ultrassônico", "umidificador_ultrassonico.png", Decimal("0.02"), "NA", "CLIMATIZACAO", "30", "BIVOLT", "PHILIPS"),
        ],
        "Desumidificador": [
            ("Desumidificador de Ar 10L/dia", "desumidificador_10l.png", Decimal("0.05"), "NA", "CLIMATIZACAO", "200", "BIVOLT", "OUTRA"),
        ],
        # Higiene e cuidados pessoais
        "Secador de cabelo": [
            ("Secador de Cabelo Profissional 2000W", "secador_2000w.png", Decimal("0.04"), "NA", "ELETRONICOS", "2000", "BIVOLT", "PHILIPS"),
        ],
        "Chapinha / Prancha": [
            ("Chapinha Alisadora Cerâmica", "chapinha_ceramica.png", Decimal("0.03"), "NA", "ELETRONICOS", "400", "BIVOLT", "PHILIPS"),
        ],
        "Barbeador elétrico": [
            ("Barbeador Elétrico Recarregável", "barbeador_recarregavel.png", Decimal("0.005"), "NA", "ELETRONICOS", "10", "BIVOLT", "PHILIPS"),
        ],
        "Escova elétrica dental": [
            ("Escova Elétrica Dental Sônica", "escova_sonica.png", Decimal("0.001"), "NA", "ELETRONICOS", "5", "BIVOLT", "ORAL-B"),
        ],
        "Aparelho de depilação": [
            ("Depilador Elétrico Bivolt", "depilador_bivolt.png", Decimal("0.005"), "NA", "ELETRONICOS", "20", "BIVOLT", "PHILIPS"),
        ],
        # Limpeza
        "Aspirador de pó": [
            ("Aspirador de Pó Vertical 1000W", "aspirador_vertical.png", Decimal("0.05"), "NA", "ELETRONICOS", "1000", "127", "ELECTROLUX"),
            ("Aspirador de Pó Portátil", "aspirador_portatil.png", Decimal("0.03"), "NA", "ELETRONICOS", "150", "BIVOLT", "BLACK+DECKER"),
        ],
        "Lavadora a vapor": [
            ("Lavadora a Vapor Portátil", "lavadora_vapor.png", Decimal("0.07"), "NA", "ELETRONICOS", "1200", "127", "OUTRA"),
        ],
        "Robô aspirador": [
            ("Robô Aspirador Inteligente", "robo_aspirador.png", Decimal("0.01"), "NA", "ELETRONICOS", "50", "BIVOLT", "SAMSUNG"),
        ],
        "Enceradeira elétrica": [
            ("Enceradeira Elétrica Doméstica", "enceradeira_domestica.png", Decimal("0.06"), "NA", "ELETRONICOS", "300", "127", "OUTRA"),
        ],
        # Eletrônicos e entretenimento
        "Televisão": [
            ("Smart TV LED 50 polegadas 4K", "tv_50_4k.png", Decimal("15.00"), "A", "ELETRONICOS", "120", "BIVOLT", "SAMSUNG"),
            ("Smart TV OLED 65 polegadas", "tv_65_oled.png", Decimal("20.00"), "A", "ELETRONICOS", "180", "BIVOLT", "LG"),
            ("Smart TV QLED 55 polegadas", "tv_55_qled.png", Decimal("18.00"), "A", "ELETRONICOS", "150", "BIVOLT", "SAMSUNG"),
        ],
        "Home Theater / Soundbar": [
            ("Soundbar com Subwoofer", "soundbar_subwoofer.png", Decimal("0.05"), "NA", "ELETRONICOS", "200", "BIVOLT", "LG"),
        ],
        "Videogame": [
            ("Console de Videogame Última Geração", "videogame_console.png", Decimal("0.10"), "NA", "ELETRONICOS", "200", "BIVOLT", "SONY"),
        ],
        "Aparelho de DVD / Blu-ray": [
            ("Leitor Blu-ray Player", "blu_ray_player.png", Decimal("0.01"), "NA", "ELETRONICOS", "25", "BIVOLT", "PHILIPS"),
        ],
        "Roteador Wi-Fi": [
            ("Roteador Wi-Fi Dual Band AC1200", "roteador_ac1200.png", Decimal("0.005"), "NA", "ELETRONICOS", "15", "BIVOLT", "TP-LINK"),
        ],
        "Computador Desktop": [
            ("Computador Desktop Gamer", "pc_gamer.png", Decimal("0.30"), "NA", "ELETRONICOS", "500", "BIVOLT", "DELL"),
        ],
        "Monitor": [
            ("Monitor LED 24 polegadas Full HD", "monitor_24_fhd.png", Decimal("0.02"), "NA", "ELETRONICOS", "30", "BIVOLT", "SAMSUNG"),
        ],
        "Notebook (carregador)": [
            ("Carregador Notebook Universal", "carregador_notebook.png", Decimal("0.01"), "NA", "ELETRONICOS", "65", "BIVOLT", "OUTRA"),
        ],
        "Impressora": [
            ("Impressora Multifuncional Tanque de Tinta", "impressora_multifuncional.png", Decimal("0.02"), "NA", "ELETRONICOS", "50", "BIVOLT", "EPSON"),
        ],
        "Caixa de som amplificada": [
            ("Caixa de Som Bluetooth Portátil", "caixa_bluetooth.png", Decimal("0.01"), "NA", "ELETRONICOS", "20", "BIVOLT", "JBL"),
        ],
        "Projetor": [
            ("Projetor Full HD 3000 Lumens", "projetor_fhd.png", Decimal("0.08"), "NA", "ELETRONICOS", "200", "BIVOLT", "EPSON"),
        ],
        "Modem de internet": [
            ("Modem Roteador Fibra Óptica", "modem_fibra.png", Decimal("0.005"), "NA", "ELETRONICOS", "10", "BIVOLT", "INTELBRAS"),
        ],
        # Iluminação e acessórios diversos
        "Luminárias de mesa": [
            ("Luminária de Mesa LED Ajustável", "luminaria_mesa.png", Decimal("0.003"), "NA", "ILUMINACAO", "10", "BIVOLT", "PHILIPS"),
        ],
        "Lâmpadas inteligentes": [
            ("Lâmpada Inteligente LED RGB", "lampada_inteligente_rgb.png", Decimal("0.008"), "A", "ILUMINACAO", "9", "BIVOLT", "POSITIVO"),
        ],
        "Carregadores de celular": [
            ("Carregador de Celular Turbo", "carregador_celular_turbo.png", Decimal("0.002"), "NA", "ELETRONICOS", "15", "BIVOLT", "SAMSUNG"),
        ],
        "Câmeras de segurança (ligadas via tomada)": [
            ("Câmera de Segurança IP Wi-Fi", "camera_ip_wifi.png", Decimal("0.005"), "NA", "ELETRONICOS", "12", "BIVOLT", "INTELBRAS"),
        ],
    }

    insert_statements = []

    for device_type, devices in realistic_devices_data.items():
        # Para cada tipo de dispositivo, gerar num_entries_per_device_type entradas
        # ou o número total de exemplos disponíveis, o que for menor.
        num_to_generate = min(num_entries_per_device_type, len(devices))
        selected_devices = random.sample(devices, num_to_generate)

        for device_data in selected_devices:
            name, icon_base, avg_kwh, procel_seal, categoria, potencia_nominal, tensao, marca = device_data

            # Adicionar um número para o nome se houver mais de uma entrada gerada do mesmo tipo
            unique_name = name
            if num_entries_per_device_type > 1:
                unique_name = f"{name} {random.randint(1, 999)}"

            icon = f"https://example.com/icons/{icon_base}" # Simula um caminho de ícone

            _name = f"'{unique_name}'"
            _icon = f"'{icon}'" if icon else 'NULL'
            _avg_kwh = f"{avg_kwh}" if avg_kwh is not None else 'NULL'
            _procel_seal = f"'{procel_seal}'"
            _categoria = f"'{categoria}'" if categoria else 'NULL'
            _potencia_nominal = f"'{potencia_nominal}'" if potencia_nominal else 'NULL'
            _tensao = f"'{tensao}'" if tensao else 'NULL'
            _marca = f"'{marca}'" if marca else 'NULL'

            insert_sql = (
                f"INSERT INTO device_catalog (name, icon, avg_kwh, procel_seal, categoria, potencia_nominal, tensao, marca) "
                f"VALUES ({_name}, {_icon}, {_avg_kwh}, {_procel_seal}, {_categoria}, {_potencia_nominal}, {_tensao}, {_marca});"
            )
            insert_statements.append(insert_sql)

    return insert_statements

if __name__ == "__main__":
    inserts = generate_realistic_device_catalog_inserts(num_entries_per_device_type=5)
    for statement in inserts:
        print(statement)