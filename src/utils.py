import pandas as pd


def rename_company(companies: pd.DataFrame, asset: str) -> str:
    a = companies.loc[asset]
    return asset + ' - ' + a.Security
