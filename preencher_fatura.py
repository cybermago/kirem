import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Seus dados de login e da fatura continuam os mesmos
DADOS_DE_LOGIN = {
    "username": "usertest",
    "password": "Turing32"
}
dados_fatura = {
    "id_profile": "1",
    "id_bill_type": "BT_CONV",
    "id_bill_number": "082025-001", 
    "id_invoice_date": "2025-07-28",
    "id_due_date": "2025-08-10",
    "id_start_period": "2025-06-25",
    "id_end_period": "2025-07-25",
    "id_days_billed": "30",
    "id_kwh_total_billed": "125",
    "id_total_cost": "135.50",
    "id_energy_charge_total": "90.15",
    "id_availability_cost_value": "0.00",
    "id_demand_charge_total": "0.00",
    "id_energy_tariff_used": "1",
    "id_applied_tariff_flag": "VERDE",
    "id_applied_tariff_flag_cost": "0.00",
    "id_flag_additional_cost_per_100kwh": "0.00",
    "id_meter_id": "98765432-1",
    "id_previous_reading": "15550",
    "id_current_reading": "15675",
    "id_meter_constant": "1.0",
    "id_next_reading_date": "2025-08-26",
    "id_icms_value": "28.00",
    "id_pis_value": "1.10",
    "id_cofins_value": "4.25",
    "id_cip_cost": "12.00",
    "id_notes": "Fatura preenchida para inspeção, sem salvar."
}

def fazer_login(driver, username, password):
    try:
        print("Tentando fazer login...")
        # CORREÇÃO: A URL de login deve apontar para a página de login
        login_url = "http://localhost:8000/billing_records/create/"
        driver.get(login_url)
        
        wait = WebDriverWait(driver, 10)
        username_field = wait.until(EC.presence_of_element_located((By.ID, "id_username")))
        password_field = driver.find_element(By.ID, "id_password")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        
        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        
        time.sleep(2)
        print("Login realizado com sucesso!")
        return True
    except Exception as e:
        print(f"ERRO durante o login: {e}")
        return False
    
# --- SCRIPT DE AUTOMAÇÃO ---
print("Iniciando automação...")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

try:
    if fazer_login(driver, DADOS_DE_LOGIN["username"], DADOS_DE_LOGIN["password"]):
    
        url = "http://localhost:8000/billing_records/create/"
        driver.get(url)
        print(f"Página {url} aberta com sucesso.")
        time.sleep(2)

        for field_id, value in dados_fatura.items():
            try:
                element = driver.find_element(By.ID, field_id)
                if element.tag_name == 'select':
                    select = Select(element)
                    select.select_by_value(value)
                    print(f"Campo SELECT '{field_id}' preenchido.")
                else:
                    element.clear() # Limpa o campo antes de preencher
                    element.send_keys(value)
                    print(f"Campo INPUT '{field_id}' preenchido.")
            except Exception:
                print(f"AVISO: Campo '{field_id}' não encontrado ou não pôde ser preenchido.")

        print("\nFormulário preenchido. O script agora vai pausar.")
        print("O navegador permanecerá aberto para sua inspeção.")
        
        # ======================================================= #
        #      ALTERAÇÃO 1: O CÓDIGO DE SUBMISSÃO FOI REMOVIDO      #
        # ======================================================= #
        # submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        # submit_button.click()
        # print("Formulário enviado com sucesso!")

        # Mantém o script pausado até você pressionar Enter no terminal
        input("Pressione Enter no terminal para fechar o navegador e encerrar o script...")

finally:
    # ======================================================= #
    #      ALTERAÇÃO 2: O COMANDO DE FECHAR FOI REMOVIDO        #
    # ======================================================= #
    # driver.quit() # Comentado para não fechar o navegador automaticamente
    print("Script encerrado pelo usuário.")
    # Fechando o driver após o input do usuário
    driver.quit()