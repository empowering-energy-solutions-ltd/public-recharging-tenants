from pathlib import Path

import numpy as np
import pandas as pd

from src.data import schema


def load_data(path: Path, csv: bool) -> pd.DataFrame | dict[str, pd.DataFrame]:
  """
  This allows the import of both .csv and excel files that have multiple different sheets using the csv boolean value.

  Arguments:
      path (Path): The path to the file to be imported.  
      csv (bool): A boolean value that is True if the file is a .csv file and False if it is an excel file.  

  Returns:
      pd.DataFrame: A pandas dataframe containing the data from the file.  
      dict[str, pd.DataFrame]: A dictionary of pandas dataframes containing the data from the different sheets of the excel file.  
  """
  if csv is True:
    dataf = pd.read_csv(path)
    return dataf
  else:
    all_sheets = pd.read_excel(path, sheet_name=None)
    #list_sheets = list(all_sheets.keys())
    dataframes = {}
    for sheet_name, df in all_sheets.items():
      dataframes[sheet_name] = df
    return dataframes


def order_gas_invoice_data(gas_invoice_path: Path) -> pd.DataFrame:
  """
  This function imports the gas invoice data and orders it into the correct format.

  Arguments:
      gas_invoice_path (Path): The path to the gas invoice file.
  
  Returns:
      pd.DataFrame: A pandas dataframe containing the gas invoice data in the correct format.
  """
  gas_invoices = load_data(path=gas_invoice_path, csv=True)
  gas_invoice_data = pd.DataFrame()
  raw_invoice_data_g = gas_invoices[[
      'mpr', 'period_from', 'consumption_kWh', 'net_charge'
  ]]
  gas_invoice_data[
      schema.InvoiceSchema.MPR] = raw_invoice_data_g['mpr'].astype(str)
  gas_invoice_data[schema.InvoiceSchema.DATE] = pd.to_datetime(
      raw_invoice_data_g['period_from'], format='%Y-%m-%d')
  gas_invoice_data[
      schema.InvoiceSchema.CONSUMPTION] = raw_invoice_data_g['consumption_kWh']
  gas_invoice_data[
      schema.InvoiceSchema.GROSS] = raw_invoice_data_g['net_charge']
  gas_invoice_data[schema.InvoiceSchema.RATE] = gas_invoice_data[
      schema.InvoiceSchema.GROSS] / gas_invoice_data[
          schema.InvoiceSchema.CONSUMPTION]
  gas_invoice_data[schema.InvoiceSchema.RATE].replace(np.inf, 0, inplace=True)
  return gas_invoice_data


def import_water(water_invoice_path: Path) -> pd.DataFrame:
  """
  This function imports the water invoice data and orders it into the correct format.

  Arguments:
      water_invoice_path (Path): The path to the water invoice file.

  Returns:
      pd.DataFrame: A pandas dataframe containing the water invoice data in the correct format.
  """
  water_invoice = load_data(path=water_invoice_path, csv=True)
  water_invoice[schema.NewHistoricSchema.MONTH] = pd.to_datetime(
      water_invoice[schema.NewHistoricSchema.MONTH], format='%Y-%m-%d')
  return water_invoice  # type: ignore


def combine_elec(elec_invoice_path: Path) -> pd.DataFrame:
  """
  This function imports the second electrical invoice and combines it with the first.

  Arguments:
      elec_invoice_path (Path): The path to the second electrical invoice file.

  Returns:
      pd.DataFrame: A pandas dataframe containing the electrical invoice data in the correct format.
  """

  raw_elec_invoices = load_data(elec_invoice_path, csv=True)
  invoice_e = raw_elec_invoices[[
      'MPAN/MPR', 'Date', 'Total Adjusted Energy Consumption (kWh)',
      'Total Net (GBP)'
  ]]
  invoice_data_e = pd.DataFrame()
  invoice_data_e[schema.InvoiceSchema.MPR] = invoice_e['MPAN/MPR'].astype(str)
  invoice_data_e[schema.InvoiceSchema.DATE] = pd.to_datetime(invoice_e['Date'],
                                                             format='%Y-%m-%d')
  invoice_data_e[schema.InvoiceSchema.CONSUMPTION] = invoice_e[
      'Total Adjusted Energy Consumption (kWh)']
  invoice_data_e[schema.InvoiceSchema.GROSS] = invoice_e['Total Net (GBP)']
  invoice_data_e[schema.InvoiceSchema.RATE] = invoice_data_e[
      schema.InvoiceSchema.GROSS] / invoice_data_e[
          schema.InvoiceSchema.CONSUMPTION]
  return invoice_data_e


def order_data(dataf: pd.DataFrame):
  """
  This function orders the data in the correct format.

  Arguments:
      dataf (pd.DataFrame): The data to be ordered.
  """
  dataf.dropna(axis=1, how='all', inplace=True)
  dataf = dataf.iloc[1:]
  dataf.columns = dataf.iloc[0]
  dataf = dataf.iloc[1:]
  dataf.drop(dataf.tail(1).index, inplace=True)


def meter_readings(path: Path) -> pd.DataFrame:
  """
  This function imports the meter readings from the site and orders it into the correct format.

  Arguments:
      path (Path): The path to the meter readings file.

  Returns:
      pd.DataFrame: A pandas dataframe containing the meter readings data in the correct format.
  """
  dataf = pd.read_csv(path)
  dataf_1 = pd.DataFrame()
  dataf_1[schema.MeterSchema.DATE] = pd.to_datetime(dataf['Datetime'],
                                                    format='%m/%d/%y')
  dataf_1[schema.MeterSchema.SITE] = dataf['Site'].astype(str)
  dataf_1[schema.MeterSchema.UTILITY] = dataf['Utility/Meter']
  dataf_1[schema.MeterSchema.SUBUTILITY] = dataf['Sub Utility']
  dataf_1[schema.MeterSchema.FLOW] = dataf['Flow'].fillna(False)
  dataf_1[
      schema.MeterSchema.PREVIOUS_READING] = dataf['Previous meter reading']
  dataf_1[
      schema.MeterSchema.PREVIOUS_DATE] = dataf['Previous meter reading date']
  dataf_1[schema.MeterSchema.PRESENT_READING] = dataf['Present meter reading']
  dataf_1[
      schema.MeterSchema.PRESENT_DATE] = dataf['Present meter reading date']
  return dataf_1
