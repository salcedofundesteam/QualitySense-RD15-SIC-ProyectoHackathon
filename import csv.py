import polars as pl
from pathlib import Path
import requests
import time

token = "Z2IZC1YIYVGLUIAI"
def historical_data(token: str):
        url = f'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol=IBM&apikey={token}'
        r = requests.get(url)
        data = r.json()
        DF = pl.DataFrame(data['data'])
        gamma = DF.select(pl.col("gamma"))
        rho = DF.select(pl.col("rho"))
        return gamma, rho
    
if __name__ == "__main__":
    while True:
        start_time = time.time()
        gamma, rho = historical_data(token)
        print("Gamma:")
        print(gamma)
        print("\tRho:")
        print(rho)
        end_time = time.time()
        time.sleep(2.4)
        print(f"\nExecution Time: {end_time - start_time} seconds")   

# print(historical_data(token))#filePath = Path.home() / 'Downloads' / ''

# scan = pl.scan_csv(
#    filePath,
#    truncate_ragged_lines=True,  # ignora líneas mal formateadas
#    ignore_errors=True            # evita que se detenga por errores
#)

