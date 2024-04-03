class ResidentialSchema:
  BUILDING = 'Property'


class CommercialSchema:
  BUILDING = 'Business'
  CONSUMPTIONMETERS = 'Consumption (m3)'
  CONVERSION = 'Conversion factor'


class GeneralValsSchema:
  BILL_MONTH = 'Billing month'
  D_PRESENT = 'Period to'
  D_PAST = 'Period from'
  M_PRESENT = 'Present reading'
  M_PAST = 'Previous reading'
  RECHARGE = 'Recharge rate (GBP/kWh)'
  WATER_RECHARGE = 'Charge Rate (£/m3)'
  CONSUMPTION = 'Consumption (MWh)'
  FIXED = 'Fixed charge (GBP)'
  NET = 'Net charge (£)'
  GROSS = 'Gross charge (£)'


class WaterBillSchema:
  BUILDING = 'Business'
  D_PRESENT = 'Period to'
  D_PAST = 'Period from'
  M_PRESENT = 'Present reading'
  M_PAST = 'Previous reading'
  CONSUMPTION = 'Consumption (kWh)'
  NET = 'Net charge (£)'
  GROSS = 'Gross charge (£)'


class MeterSchema:
  DATE = 'Period from'
  SITE = 'Residential/Commercial site'
  PREVIOUS_READING = 'Previous meter reading'
  PRESENT_READING = 'Present meter reading'
  PREVIOUS_DATE = 'Previous meter reading date'
  PRESENT_DATE = 'Present meter reading date'
  UTILITY = 'Utility/Meter'
  SUBUTILITY = 'Sub meter'
  FLOW = 'Flow'
  CONSUMPTION = 'Corrected consumption (kWh)'
  CHARGE = 'Consumption charge (GBP)'
  N_CHARGE = 'Net charge (GBP)'
  G_CHARGE = 'Gross charge (GBP)'
  READING = 'Reading multiplier'


class IdentifierSchema:
  MPR = 'MPR'
  MPAN = 'MPAN'
  WATER = 'Water_meter'


class InvoiceSchema:
  MPR = 'MPAN/MPR'
  DATE = 'Bill period'
  CONSUMPTION = 'Consumption (kWh)'
  GROSS = 'Consumption Charge (£)'
  RATE = 'Recharge rate (GBP/kWh)'


class HistoricSchema:
  LOCATION = 'location'
  WATER = 'water'
  ELECTRIC_1 = 'elec'
  ELECTRIC_2 = 'electricity'
  GAS = 'gas'
  CONSUMP_M = 'cons (m3)'
  CONSUMP_KWH = 'cons (kWh)'
  COST = 'cost'
  MONTH = 'month'


class NewHistoricSchema:
  LOCATION = 'Location'
  WATER = 'Water'
  ELECTRIC = 'Electric'
  GAS = 'Gas'
  CONSUMP_M = 'Consumption (m3)'
  CONSUMP_KWH = 'Consumption (kWh)'
  COST = 'Cost (£)'
  MONTH = 'Date'
