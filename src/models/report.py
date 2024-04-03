from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

# from src.common import enums
from src.data import import_data, schema


@dataclass
class Site:
  """
  The site class generates the invoices for each tenant of the main site.

  Attributes:
    name str:
        The name of the site.
    id_mappings dict[str, dict[str, str]]:
        A dictionary containing the mappings of the tenants to the site meters.
    fixed_rate_mappings dict[str, dict[str, float]]:
        A dictionary containing the mappings of the tenants to their fixed rates.
    readings_multiplier dict[str, dict[str, float]]:
        A dictionary containing the mappings of the tenants to the multipliers for their meter readings.
    commercial_list list[str]"
        A list of the tenants that are commercial.
    reading_path Path:
        The path to the meter readings file.
    water_path Path:
        The path to the water invoice file.
    gas_path Path:
        The path to the gas invoice file.
    electric_path_1 Path:
        The path to the first electricity invoice file.
    electric_path_2 Path:
        The path to the second electricity invoice file.  
    historical_charges_path Path:
        The path to the historical charges file.
    historical_readings_path Path:
        The path to the historical readings file.
    save_folder Path:
        The path to the folder where the results will be saved.

  Methods:
    create_saving_path:
        This function creates the path where the results will be saved.
    get_data:
        This function imports the meter readings file.
    merge_utility_rows:
        This function merges the rows of the meter readings file that correspond to the same meter.
    calculate_energy_consumption:
        This function calculates the energy consumption of a meter.
    outflow_conversion:
        This function converts the outflow readings to negative values.
    reorder_data:
        This function reorders the meter readings file.
    apply_id_mappings:
        This function applies the id mappings to the meter readings file.
    invoice_history:
        This function imports the invoice history files.
    apply_recharge_rates:
        This function applies the recharge rates to the consumption data.
    apply_fixed_mappings:
        Applies fixed charges to the data
    apply_readings_multiplier:
        Applies readings multiplier to the dataframe
    calculate_charges:
        Calculates the net and gross charge before VAT
    new_form:
        Creates the new form for next month to be filled out
    historical_charges:
        Adds the current months charges to the historical charges file
    historical_readings:
        Adds the current months readings to the historical readings file
    split_dataframe_by_commercial:
        Splits the dataframe into two based on whether the tenant is residencial or commercial
    recharging_tenants:
        Recharges the tenants. Main function to be called.
  """

  name: str
  id_mappings: dict[str, dict[str, str]]
  fixed_rate_mappings: dict[str, dict[str, float]]
  readings_multiplier: dict[str, dict[str, float]]
  commercial_list: list[str]
  reading_path: Path
  water_path: Path
  gas_path: Path
  electric_path: Path
  historical_charges_path: Path
  historical_readings_path: Path
  save_folder: Path

  def create_saving_path(self, parent_folder: Path,
                         recharging_date: datetime) -> None:
    """
    This function creates the path where the results will be saved.

    Arguments:
        parent_folder (Path): The path to the parent folder where the results will be saved.  
    `recharging_date (datetime): The date of the recharging.  
    """
    forecast_from_str = recharging_date.strftime("%B %Y")
    temp_path_export_results = parent_folder / f'{self.name}_{forecast_from_str.replace(" ","_")}'
    temp_path_export_results.mkdir(parents=True, exist_ok=True)
    self.save_folder = temp_path_export_results

  def get_data(self) -> pd.DataFrame:
    """
    This function imports the meter readings file.

    Returns:
        pd.DataFrame: The meter readings file.
    """

    return import_data.meter_readings(self.reading_path)

  def merge_utility_rows(self) -> pd.DataFrame:
    """
    This function merges the rows of the meter readings file that correspond to the same meter.

    Returns:
        pd.DataFrame: The meter readings file with the rows merged.
    """
    dataf = self.get_data()
    return dataf.groupby([
        schema.MeterSchema.DATE, schema.MeterSchema.SITE,
        schema.MeterSchema.UTILITY, schema.MeterSchema.FLOW
    ],
                         as_index=False).agg({
                             schema.MeterSchema.PREVIOUS_READING:
                             'sum',
                             schema.MeterSchema.PRESENT_READING:
                             'sum'
                         })

  def calculate_energy_consumption(self, row) -> float:
    """ Calculates the energy consumption of a meter.

    Arguments:
        row (pd.Series): A row of the meter readings file.

    Returns:
        float: The consumption of the meter.
    """
    reading_multiplier = self.readings_multiplier
    site = row[schema.MeterSchema.SITE]
    utility_type = row[schema.MeterSchema.UTILITY]
    prev_reading = row[schema.MeterSchema.PREVIOUS_READING]
    present_reading = row[schema.MeterSchema.PRESENT_READING]
    try:
      multiplier = reading_multiplier[site][utility_type]
    except KeyError:
      consumption = (present_reading - prev_reading)
    else:
      consumption = (present_reading - prev_reading) * multiplier
    return consumption

  def outflow_conversion(self, row) -> float:
    """
    This function converts the outflow readings to negative values.

    Arguments:
        row (pd.Series): A row of the meter readings file.

    Returns:
        float: The consumption of the meter.
    """
    flow = row[schema.MeterSchema.FLOW]
    consumption = row[schema.MeterSchema.CONSUMPTION]
    if flow:
      consumption *= -1
    else:
      pass
    return consumption

  def reorder_data(self) -> pd.DataFrame:  # Sums consumption
    """
    This function reorders the meter readings file.

    Returns:
        pd.DataFrame: The meter readings file reordered.
    """
    dataf = self.merge_utility_rows()
    dataf[schema.MeterSchema.CONSUMPTION] = dataf.apply(
        self.calculate_energy_consumption, axis=1)
    dataf[schema.MeterSchema.CONSUMPTION] = dataf.apply(
        self.outflow_conversion, axis=1)
    dataf = dataf.groupby([
        schema.MeterSchema.DATE, schema.MeterSchema.SITE,
        schema.MeterSchema.UTILITY
    ],
                          as_index=False).agg(
                              {schema.MeterSchema.CONSUMPTION: 'sum'})
    return dataf

  def apply_id_mappings(self) -> pd.DataFrame:
    """
    This function applies the id mappings to the meter readings file.

    Returns:
        pd.DataFrame: The meter readings file with the id mappings applied.
    """
    id_mappings = self.id_mappings
    dataf = self.reorder_data()
    for index, row in dataf.iterrows():
      site_name = row[schema.MeterSchema.SITE]
      utility = row[schema.MeterSchema.UTILITY]
      if site_name.startswith('House'):
        if utility == 'G':
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings['House']['mpr']
        elif utility == 'E':
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings['House']['mpan']
        elif utility == 'W':
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings['House']['water']
      elif site_name in id_mappings:
        if utility == 'G' and 'mpr' in id_mappings[site_name]:
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings[site_name]['mpr']
        elif utility == 'E' and 'mpan' in id_mappings[site_name]:
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings[site_name]['mpan']
        elif utility == 'W' and 'water' in id_mappings[site_name]:
          dataf.loc[index,
                    schema.InvoiceSchema.MPR] = id_mappings[site_name]['water']
    return dataf

  def invoice_history(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    This function imports the invoice history files.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: The gas, electricity and water invoice history files.
    """
    gas_invoice = import_data.order_gas_invoice_data(self.gas_path)
    elec_invoice = import_data.combine_elec(
        elec_invoice_path=self.electric_path)
    water_invoice = import_data.import_water(self.water_path)
    return gas_invoice, elec_invoice, water_invoice

  def apply_recharge_rates(self, days_range=1) -> pd.DataFrame:
    """
    This function applies the recharge rates to the consumption data.

    Arguments:
        days_range (Optional[int]): The number of days to look back for the recharge rate, by default 1.

    Returns:
        pd.DataFrame: The consumption data with the recharge rates applied.
    """
    electric_data, gas_data, water_data = self.invoice_history()
    dataf = self.apply_id_mappings()
    recharge_rates = {}
    for index, row in electric_data.iterrows():
      recharge_rates[(row[schema.InvoiceSchema.MPR],
                      row[schema.InvoiceSchema.DATE]
                      )] = row[schema.GeneralValsSchema.RECHARGE]
    for index, row in gas_data.iterrows():
      recharge_rates[(row[schema.InvoiceSchema.MPR],
                      row[schema.InvoiceSchema.DATE]
                      )] = row[schema.GeneralValsSchema.RECHARGE]
    for index, row in water_data.iterrows():
      recharge_rates[(row[schema.InvoiceSchema.MPR],
                      row[schema.NewHistoricSchema.MONTH]
                      )] = row[schema.GeneralValsSchema.RECHARGE]
    for index, row in dataf.iterrows():
      mpan_mpr = row[schema.InvoiceSchema.MPR]
      date = row[schema.MeterSchema.DATE]
      # Get the date range
      start_date = date - pd.Timedelta(days_range, unit='D')
      end_date = date + pd.Timedelta(days_range, unit='D')
      # Filter rows in table_1 and table_2 to the given date range
      matching_rows_1 = electric_data.loc[
          (electric_data[schema.InvoiceSchema.MPR] == mpan_mpr)
          & (electric_data[schema.InvoiceSchema.DATE].between(
              start_date, end_date))]
      matching_rows_2 = gas_data.loc[
          (gas_data[schema.InvoiceSchema.MPR] == mpan_mpr) &
          (gas_data[schema.InvoiceSchema.DATE].between(start_date, end_date))]
      matching_rows_3 = water_data.loc[
          (water_data[schema.InvoiceSchema.MPR] == mpan_mpr) & (water_data[
              schema.NewHistoricSchema.MONTH].between(start_date, end_date))]
      # Combine matching rows into one dataframe
      matching_rows = pd.concat(
          [matching_rows_1, matching_rows_2, matching_rows_3])
      if not matching_rows.empty:
        recharge_rate = matching_rows.iloc[0][
            schema.GeneralValsSchema.RECHARGE]
        dataf.loc[index, schema.GeneralValsSchema.RECHARGE] = recharge_rate
    return dataf

  def apply_fixed_mappings(self) -> pd.DataFrame:
    """
    Applies fixed charges to the data
    
    Returns:
        pd.DataFrame: Dataframe with fixed charges applied
    """
    fixed_charges_mappings = self.fixed_rate_mappings
    dataf = self.apply_recharge_rates().fillna(0)
    dataf[schema.GeneralValsSchema.FIXED] = 0
    for index, row in dataf.iterrows():
      site_name = row[schema.MeterSchema.SITE]
      utility = row[schema.MeterSchema.UTILITY]
      if site_name in fixed_charges_mappings:
        if utility == 'G' and 'Gas' in fixed_charges_mappings[site_name]:
          dataf.at[index, schema.GeneralValsSchema.
                   FIXED] = fixed_charges_mappings[site_name]['Gas']
        elif utility == 'E' and 'Electric' in fixed_charges_mappings[site_name]:
          dataf.at[index, schema.GeneralValsSchema.
                   FIXED] = fixed_charges_mappings[site_name]['Electric']
        elif utility == 'W' and 'Water' in fixed_charges_mappings[site_name]:
          dataf.at[index, schema.GeneralValsSchema.
                   FIXED] = fixed_charges_mappings[site_name]['Water']
    return dataf

  def apply_readings_multiplier(self) -> pd.DataFrame:
    """
    Applies readings multiplier to the dataframe
    
    Returns:
        pd.DataFrame: Dataframe with readings multiplier applied
    """
    readings_multiplier_mappings = self.readings_multiplier
    dataf = self.apply_fixed_mappings().fillna(0)
    dataf[schema.MeterSchema.READING] = 0
    for index, row in dataf.iterrows():
      site_name = row[schema.MeterSchema.SITE]
      utility = row[schema.MeterSchema.UTILITY]
      if site_name in readings_multiplier_mappings:
        if utility == 'G' and 'G' in readings_multiplier_mappings[site_name]:
          dataf.at[index, schema.MeterSchema.
                   READING] = readings_multiplier_mappings[site_name]['G']
        elif utility == 'E' and 'E' in readings_multiplier_mappings[site_name]:
          dataf.at[index, schema.MeterSchema.
                   READING] = readings_multiplier_mappings[site_name]['E']
    return dataf

  def calculate_charges(self) -> pd.DataFrame:
    """
    Calculates the net and gross charge before VAT

    Returns:
        pd.DataFrame: Dataframe with net and gross charge before VAT calculated
    """
    dataf = self.apply_readings_multiplier()
    dataf[schema.MeterSchema.
          N_CHARGE] = dataf[schema.GeneralValsSchema.RECHARGE] * dataf[
              schema.MeterSchema.CONSUMPTION]
    dataf[schema.MeterSchema.G_CHARGE] = dataf[
        schema.MeterSchema.N_CHARGE] + dataf[schema.GeneralValsSchema.FIXED]
    return dataf.round(6)

  def new_form(self) -> pd.DataFrame:
    """
    Creates the new form for next month to be filled out

    Returns:
        pd.DataFrame: Dataframe with the new form for next month to be filled out
    """
    dataf = self.get_data()
    form = pd.DataFrame(columns=[
        schema.MeterSchema.SITE, schema.MeterSchema.UTILITY,
        schema.MeterSchema.SUBUTILITY, schema.MeterSchema.FLOW,
        schema.MeterSchema.PREVIOUS_READING, schema.MeterSchema.PREVIOUS_DATE,
        schema.MeterSchema.PRESENT_READING, schema.MeterSchema.PRESENT_DATE
    ])
    form[schema.MeterSchema.SITE] = dataf[schema.MeterSchema.SITE]
    form[schema.MeterSchema.UTILITY] = dataf[schema.MeterSchema.UTILITY]
    form[schema.MeterSchema.SUBUTILITY] = dataf[schema.MeterSchema.SUBUTILITY]
    form[schema.MeterSchema.FLOW] = dataf[schema.MeterSchema.FLOW]
    form[schema.MeterSchema.PREVIOUS_READING] = dataf[
        schema.MeterSchema.PRESENT_READING]
    form[schema.MeterSchema.PREVIOUS_DATE] = dataf[
        schema.MeterSchema.PRESENT_DATE]
    form.index = dataf[schema.MeterSchema.DATE] + pd.DateOffset(months=1)
    return form.to_csv(self.save_folder / 'new_form.csv', encoding='utf-8-sig')

  def historical_charges(
      self):  # Adds the current months charges to the historical charges file
    """
    Adds the current months charges to the historical charges file

    """
    dataf = self.calculate_charges()
    historical_tenant_charges = pd.read_csv(self.historical_charges_path)
    historical_tenant_charges = pd.concat([dataf, historical_tenant_charges],
                                          ignore_index=True)
    historical_tenant_charges = historical_tenant_charges.drop(
        columns=['Unnamed: 0'])
    historical_tenant_charges.to_csv(self.save_folder /
                                     'historical_charges.csv',
                                     encoding='utf-8-sig')

  def historical_readings(self):
    """
    Adds the current months readings to the historical readings file
    """
    dataf = self.get_data()
    historical_tenant_readings = pd.read_csv(self.historical_readings_path)
    historical_tenant_readings = pd.concat([dataf, historical_tenant_readings],
                                           ignore_index=True)
    historical_tenant_readings = historical_tenant_readings.drop(
        columns=['Unnamed: 0'])
    historical_tenant_readings.to_csv(self.save_folder /
                                      'historical_readings.csv',
                                      encoding='utf-8-sig')

  def split_dataframe_by_commercial(self):
    """
    Splits the dataframe into two based on whether the tenant is residencial or commercial

    """
    dataf = self.calculate_charges()
    commercial_df = dataf[dataf['Residential/Commercial site'].isin(
        self.commercial_list)]
    non_commercial_df = dataf[~dataf['Residential/Commercial site'].
                              isin(self.commercial_list)]
    commercial_df.to_csv(self.save_folder / 'commercial_charges.csv',
                         encoding='utf-8-sig')
    non_commercial_df.to_csv(self.save_folder / 'resident_charges.csv',
                             encoding='utf-8-sig')

  def recharging_tenants(self):
    """
    Recharges the tenants. Main function to be called.

    """
    self.split_dataframe_by_commercial()
    self.new_form()
    self.historical_charges()
    self.historical_readings()
    print('Recharging forms complete. Have a nice day.')
