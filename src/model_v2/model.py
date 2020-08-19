"""Model used to construct and solve NEMDE approximation"""

import os
import json
import time

import pyomo.environ as pyo

try:
    from utils.data import parse_case_data_json
    from utils.loaders import load_dispatch_interval_json

    from components.expressions.cost_functions import define_cost_function_expressions
    from components.expressions.constraint_violation import define_constraint_violation_penalty_expressions
    from components.expressions.aggregate_power import define_aggregate_power_expressions
    from components.expressions.generic_constraints import define_generic_constraint_expressions

    from components.constraints.offers import define_offer_constraints
    from components.constraints.units import define_unit_constraints
    from components.constraints.regions import define_region_constraints
    from components.constraints.interconnectors import define_interconnector_constraints
    from components.constraints.generic_constraints import define_generic_constraints
    from components.constraints.loss import define_loss_model_constraints

    # from components.constraints.fcas import define_fcas_constraints
    from components.constraints.fcas_v2 import define_fcas_constraints

    import utils.solution
    import utils.analysis
except ModuleNotFoundError:
    from .utils.data import parse_case_data_json
    from .utils.loaders import load_dispatch_interval_json

    from .components.expressions.cost_functions import define_cost_function_expressions
    from .components.expressions.constraint_violation import define_constraint_violation_penalty_expressions
    from .components.expressions.aggregate_power import define_aggregate_power_expressions
    from .components.expressions.generic_constraints import define_generic_constraint_expressions

    from .components.constraints.offers import define_offer_constraints
    from .components.constraints.units import define_unit_constraints
    from .components.constraints.regions import define_region_constraints
    from .components.constraints.interconnectors import define_interconnector_constraints
    from .components.constraints.generic_constraints import define_generic_constraints
    from .components.constraints.loss import define_loss_model_constraints

    # from .components.constraints.fcas import define_fcas_constraints
    from .components.constraints.fcas_v2 import define_fcas_constraints

    # import .utils.solution
    # import .utils.analysis


class NEMDEModel:
    def __init__(self):
        pass

    @staticmethod
    def define_sets(m, data):
        """Define sets"""

        # NEM regions
        m.S_REGIONS = pyo.Set(initialize=data['S_REGIONS'])

        # Market participants (generators and loads)
        m.S_TRADERS = pyo.Set(initialize=data['S_TRADERS'])

        # Semi-dispatchable traders
        m.S_TRADERS_SEMI_DISPATCH = pyo.Set(initialize=data['S_TRADERS_SEMI_DISPATCH'])

        # Trader offer types
        m.S_TRADER_OFFERS = pyo.Set(initialize=data['S_TRADER_OFFERS'])

        # Trader FCAS offers
        m.S_TRADER_FCAS_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_OFFERS'])

        # Trader energy offers
        m.S_TRADER_ENERGY_OFFERS = pyo.Set(initialize=data['S_TRADER_ENERGY_OFFERS'])

        # Trader unavailable FCAS offers
        m.S_TRADER_FCAS_UNAVAILABLE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_UNAVAILABLE_OFFERS'])

        # Trader available FCAS offers
        m.S_TRADER_FCAS_AVAILABLE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_AVAILABLE_OFFERS'])

        # # Trader offer subsets used when formulating FCAS constraints
        m.S_TRADER_FCAS_R5RE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_R5RE_OFFERS'])
        m.S_TRADER_FCAS_R6SE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_R6SE_OFFERS'])
        m.S_TRADER_FCAS_R60S_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_R60S_OFFERS'])
        m.S_TRADER_FCAS_R5MI_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_R5MI_OFFERS'])
        m.S_TRADER_FCAS_L5RE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_L5RE_OFFERS'])
        m.S_TRADER_FCAS_L6SE_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_L6SE_OFFERS'])
        m.S_TRADER_FCAS_L60S_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_L60S_OFFERS'])
        m.S_TRADER_FCAS_L5MI_OFFERS = pyo.Set(initialize=data['S_TRADER_FCAS_L5MI_OFFERS'])

        # m.S_TRADER_FCAS_AVAIL_R5RE_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5RE_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_R5RE_R6SE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5RE_R6SE'])
        # m.S_TRADER_FCAS_AVAIL_R5RE_R60S = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5RE_R60S'])
        # m.S_TRADER_FCAS_AVAIL_R5RE_R5MI = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5RE_R5MI'])
        # m.S_TRADER_FCAS_AVAIL_L5RE_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5RE_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_L5RE_L6SE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5RE_L6SE'])
        # m.S_TRADER_FCAS_AVAIL_L5RE_L60S = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5RE_L60S'])
        # m.S_TRADER_FCAS_AVAIL_L5RE_L5MI = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5RE_L5MI'])
        # m.S_TRADER_FCAS_AVAIL_R6SE_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R6SE_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_R6SE_R5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R6SE_R5RE'])
        # m.S_TRADER_FCAS_AVAIL_R60S_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R60S_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_R60S_R5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R60S_R5RE'])
        # m.S_TRADER_FCAS_AVAIL_R5MI_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5MI_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_R5MI_R5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_R5MI_R5RE'])
        # m.S_TRADER_FCAS_AVAIL_L6SE_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L6SE_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_L6SE_L5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L6SE_L5RE'])
        # m.S_TRADER_FCAS_AVAIL_L60S_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L60S_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_L60S_L5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L60S_L5RE'])
        # m.S_TRADER_FCAS_AVAIL_L5MI_ENERGY = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5MI_ENERGY'])
        # m.S_TRADER_FCAS_AVAIL_L5MI_L5RE = pyo.Set(initialize=data['S_TRADER_FCAS_AVAIL_L5MI_L5RE'])

        # Generic constraints
        m.S_GENERIC_CONSTRAINTS = pyo.Set(initialize=data['S_GENERIC_CONSTRAINTS'])

        # Generic constraints trader pyo.Variables
        m.S_GC_TRADER_VARS = pyo.Set(initialize=data['S_GC_TRADER_VARS'])

        # Generic constraint interconnector pyo.Variables
        m.S_GC_INTERCONNECTOR_VARS = pyo.Set(initialize=data['S_GC_INTERCONNECTOR_VARS'])

        # Generic constraint region pyo.Variables
        m.S_GC_REGION_VARS = pyo.Set(initialize=data['S_GC_REGION_VARS'])

        # Price / quantity band index
        m.S_BANDS = pyo.RangeSet(1, 10, 1)

        # Market Network Service Providers (interconnectors that bid into the market)
        m.S_MNSPS = pyo.Set(initialize=data['S_MNSPS'])

        # MNSP offer types
        m.S_MNSP_OFFERS = pyo.Set(initialize=data['S_MNSP_OFFERS'])

        # All interconnectors (interconnector_id)
        m.S_INTERCONNECTORS = pyo.Set(initialize=data['S_INTERCONNECTORS'])

        # Interconnector loss model breakpoints
        m.S_INTERCONNECTOR_LOSS_MODEL_BREAKPOINTS = pyo.Set(initialize=data['S_INTERCONNECTOR_LOSS_MODEL_BREAKPOINTS'])

        # Interconnector loss model intervals
        m.S_INTERCONNECTOR_LOSS_MODEL_INTERVALS = pyo.Set(initialize=data['S_INTERCONNECTOR_LOSS_MODEL_INTERVALS'])

        return m

    @staticmethod
    def define_parameters(m, data):
        """Define model parameters"""

        # Price bands for traders (generators / loads)
        m.P_TRADER_PRICE_BAND = pyo.Param(m.S_TRADER_OFFERS, m.S_BANDS, initialize=data['P_TRADER_PRICE_BAND'])

        # Quantity bands for traders (generators / loads)
        m.P_TRADER_QUANTITY_BAND = pyo.Param(m.S_TRADER_OFFERS, m.S_BANDS, initialize=data['P_TRADER_QUANTITY_BAND'])

        # Max available output for given trader
        m.P_TRADER_MAX_AVAILABLE = pyo.Param(m.S_TRADER_OFFERS, initialize=data['P_TRADER_MAX_AVAILABLE'])

        # Initial MW output for generators / loads
        m.P_TRADER_INITIAL_MW = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_INITIAL_MW'])

        # UIGF for semi-dispatchable plant
        m.P_TRADER_UIGF = pyo.Param(m.S_TRADERS_SEMI_DISPATCH, initialize=data['P_TRADER_UIGF'])

        # Trader HMW and LMW
        m.P_TRADER_HMW = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_HMW'])
        m.P_TRADER_LMW = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_LMW'])

        # Trader AGC status
        m.P_TRADER_AGC_STATUS = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_AGC_STATUS'])

        # Trader semi-dispatch status
        m.P_TRADER_SEMI_DISPATCH_STATUS = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_SEMI_DISPATCH_STATUS'])

        # Trader region
        m.P_TRADER_REGION = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_REGION'])

        # Trader ramp up and down rates
        m.P_TRADER_PERIOD_RAMP_UP_RATE = pyo.Param(m.S_TRADER_ENERGY_OFFERS,
                                                   initialize=data['P_TRADER_PERIOD_RAMP_UP_RATE'])
        m.P_TRADER_PERIOD_RAMP_DOWN_RATE = pyo.Param(m.S_TRADER_ENERGY_OFFERS,
                                                     initialize=data['P_TRADER_PERIOD_RAMP_DOWN_RATE'])

        # Trader FCAS enablement min
        m.P_TRADER_FCAS_ENABLEMENT_MIN = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                   initialize={k: v['EnablementMin'] for k, v in
                                                               data['preprocessed']['FCAS_TRAPEZIUM_SCALED'].items()})

        # Trader FCAS low breakpoint
        m.P_TRADER_FCAS_LOW_BREAKPOINT = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                   initialize={k: v['LowBreakpoint'] for k, v in
                                                               data['preprocessed']['FCAS_TRAPEZIUM_SCALED'].items()})

        # Trader FCAS high breakpoint
        m.P_TRADER_FCAS_HIGH_BREAKPOINT = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                    initialize={k: v['HighBreakpoint'] for k, v in
                                                                data['preprocessed']['FCAS_TRAPEZIUM_SCALED'].items()})

        # Trader FCAS enablement max
        m.P_TRADER_FCAS_ENABLEMENT_MAX = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                   initialize={k: v['EnablementMax'] for k, v in
                                                               data['preprocessed']['FCAS_TRAPEZIUM_SCALED'].items()})

        # Trader FCAS max available
        m.P_TRADER_FCAS_MAX_AVAILABLE = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                  initialize={k: v['MaxAvail'] for k, v in
                                                              data['preprocessed']['FCAS_TRAPEZIUM_SCALED'].items()})

        # Trader FCAS availability
        m.P_TRADER_FCAS_AVAILABILITY = pyo.Param(m.S_TRADER_FCAS_OFFERS,
                                                 initialize=data['preprocessed']['FCAS_AVAILABILITY'])

        # Trader type  TODO: check trader {'GENERATOR', 'LOAD', 'NORMALLY_ON_LOAD'}
        m.P_TRADER_TYPE = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_TYPE'])

        # Trader SCADA ramp up and down rates
        m.P_TRADER_SCADA_RAMP_UP_RATE = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_SCADA_RAMP_UP_RATE'])
        m.P_TRADER_SCADA_RAMP_DOWN_RATE = pyo.Param(m.S_TRADERS, initialize=data['P_TRADER_SCADA_RAMP_DOWN_RATE'])

        # Interconnector 'to' and 'from' regions
        m.P_INTERCONNECTOR_TO_REGION = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_TO_REGION'])
        m.P_INTERCONNECTOR_FROM_REGION = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_FROM_REGION'])

        # Interconnector lower and upper limits - NOTE: these are absolute values (lower limit is positive)
        m.P_INTERCONNECTOR_LOWER_LIMIT = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_LOWER_LIMIT'])
        m.P_INTERCONNECTOR_UPPER_LIMIT = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_UPPER_LIMIT'])

        # Interconnector MNSP status
        m.P_INTERCONNECTOR_MNSP_STATUS = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_MNSP_STATUS'])

        # Interconnector loss share
        m.P_INTERCONNECTOR_LOSS_SHARE = pyo.Param(m.S_INTERCONNECTORS, initialize=data['P_INTERCONNECTOR_LOSS_SHARE'])

        # Interconnector initial loss estimate
        m.P_INTERCONNECTOR_INITIAL_LOSS_ESTIMATE = pyo.Param(m.S_INTERCONNECTORS,
                                                             initialize=data['P_INTERCONNECTOR_INITIAL_LOSS_ESTIMATE'])

        # Interconnector loss model segment limit
        m.P_INTERCONNECTOR_LOSS_MODEL_BREAKPOINT_X = pyo.Param(
            m.S_INTERCONNECTOR_LOSS_MODEL_BREAKPOINTS, initialize=data['P_INTERCONNECTOR_LOSS_MODEL_BREAKPOINT_X'])

        # Interconnector loss model segment factor
        m.P_INTERCONNECTOR_LOSS_MODEL_BREAKPOINT_Y = pyo.Param(
            m.S_INTERCONNECTOR_LOSS_MODEL_BREAKPOINTS, initialize=data['P_INTERCONNECTOR_LOSS_MODEL_BREAKPOINT_Y'])

        # Observed interconnector loss (obtained from NEMDE solution)
        m.P_INTERCONNECTOR_SOLUTION_LOSS = pyo.Param(m.S_INTERCONNECTORS,
                                                     initialize=data['P_INTERCONNECTOR_SOLUTION_LOSS'])

        # Price bands for MNSPs
        m.P_MNSP_PRICE_BAND = pyo.Param(m.S_MNSP_OFFERS, m.S_BANDS, initialize=data['P_MNSP_PRICE_BAND'])

        # Quantity bands for MNSPs
        m.P_MNSP_QUANTITY_BAND = pyo.Param(m.S_MNSP_OFFERS, m.S_BANDS, initialize=data['P_MNSP_QUANTITY_BAND'])

        # Max available output for given MNSP
        m.P_MNSP_MAX_AVAILABLE = pyo.Param(m.S_MNSP_OFFERS, initialize=data['P_MNSP_MAX_AVAILABLE'])

        # MNSP 'to' and 'from' region loss factor
        m.P_MNSP_TO_REGION_LF = pyo.Param(m.S_MNSPS, initialize=data['P_MNSP_TO_REGION_LF'])
        m.P_MNSP_FROM_REGION_LF = pyo.Param(m.S_MNSPS, initialize=data['P_MNSP_FROM_REGION_LF'])

        # MNSP loss price
        m.P_MNSP_LOSS_PRICE = pyo.Param(initialize=data['P_MNSP_LOSS_PRICE'])

        # Initial region demand
        m.P_REGION_INITIAL_DEMAND = pyo.Param(m.S_REGIONS, initialize=data['P_REGION_INITIAL_DEMAND'])

        # Region aggregate dispatch error (ADE)
        m.P_REGION_ADE = pyo.Param(m.S_REGIONS, initialize=data['P_REGION_ADE'])

        # Region demand forecast increment (DF)
        m.P_REGION_DF = pyo.Param(m.S_REGIONS, initialize=data['P_REGION_DF'])

        # Region fixed demand (obtained from case solution)
        m.P_REGION_FIXED_DEMAND = pyo.Param(m.S_REGIONS, initialize=data['P_REGION_FIXED_DEMAND'])

        # Generic constraint RHS
        m.P_GC_RHS = pyo.Param(m.S_GENERIC_CONSTRAINTS, initialize=data['P_GC_RHS'])

        # Generic constraint type
        m.P_GC_TYPE = pyo.Param(m.S_GENERIC_CONSTRAINTS, initialize=data['P_GC_TYPE'])

        # Generic constraint violation factors
        m.P_CVF_GC = pyo.Param(m.S_GENERIC_CONSTRAINTS, initialize=data['P_CVF_GC'])

        # Value of lost load
        m.P_CVF_VOLL = pyo.Param(initialize=data['P_CVF_VOLL'])

        # Energy deficit price
        m.P_CVF_ENERGY_DEFICIT_PRICE = pyo.Param(initialize=data['P_CVF_ENERGY_DEFICIT_PRICE'])

        # Energy surplus price
        m.P_CVF_ENERGY_SURPLUS_PRICE = pyo.Param(initialize=data['P_CVF_ENERGY_SURPLUS_PRICE'])

        # Ramp-rate constraint violation factor
        m.P_CVF_RAMP_RATE_PRICE = pyo.Param(initialize=data['P_CVF_RAMP_RATE_PRICE'])

        # Capacity price (assume for constraint ensuring max available capacity not exceeded)
        m.P_CVF_CAPACITY_PRICE = pyo.Param(initialize=data['P_CVF_CAPACITY_PRICE'])

        # Offer price (assume for constraint ensuring band offer amounts are not exceeded)
        m.P_CVF_OFFER_PRICE = pyo.Param(initialize=data['P_CVF_OFFER_PRICE'])

        # MNSP offer price (assumed for constraint ensuring MNSP band offers are not exceeded)
        m.P_CVF_MNSP_OFFER_PRICE = pyo.Param(initialize=data['P_CVF_MNSP_OFFER_PRICE'])

        # MNSP ramp rate price (not sure what this applies to - unclear what MNSP ramp rates are)
        m.P_CVF_MNSP_RAMP_RATE_PRICE = pyo.Param(initialize=data['P_CVF_MNSP_RAMP_RATE_PRICE'])

        # MNSP capacity price (assume for constraint ensuring max available capacity not exceeded)
        m.P_CVF_MNSP_CAPACITY_PRICE = pyo.Param(initialize=data['P_CVF_MNSP_CAPACITY_PRICE'])

        # Ancillary services profile price (assume for constraint ensure FCAS trapezium not violated)
        m.P_CVF_AS_PROFILE_PRICE = pyo.Param(initialize=data['P_CVF_AS_PROFILE_PRICE'])

        # Ancillary services max available price (assume for constraint ensure max available amount not exceeded)
        m.P_CVF_AS_MAX_AVAIL_PRICE = pyo.Param(initialize=data['P_CVF_AS_MAX_AVAIL_PRICE'])

        # Ancillary services enablement min price (assume for constraint ensure FCAS > enablement min if active)
        m.P_CVF_AS_ENABLEMENT_MIN_PRICE = pyo.Param(initialize=data['P_CVF_AS_ENABLEMENT_MIN_PRICE'])

        # Ancillary services enablement max price (assume for constraint ensure FCAS < enablement max if active)
        m.P_CVF_AS_ENABLEMENT_MAX_PRICE = pyo.Param(initialize=data['P_CVF_AS_ENABLEMENT_MAX_PRICE'])

        # Interconnector power flow violation price
        m.P_CVF_INTERCONNECTOR_PRICE = pyo.Param(initialize=data['P_CVF_INTERCONNECTOR_PRICE'])

        return m

    @staticmethod
    def define_variables(m):
        """Define model pyo.Variables"""

        # Offers for each quantity band
        m.V_TRADER_OFFER = pyo.Var(m.S_TRADER_OFFERS, m.S_BANDS, within=pyo.NonNegativeReals)
        m.V_MNSP_OFFER = pyo.Var(m.S_MNSP_OFFERS, m.S_BANDS, within=pyo.NonNegativeReals)

        # Total MW offer for each offer type
        m.V_TRADER_TOTAL_OFFER = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_MNSP_TOTAL_OFFER = pyo.Var(m.S_MNSP_OFFERS, within=pyo.NonNegativeReals)

        # Generic constraint pyo.Variables
        m.V_GC_TRADER = pyo.Var(m.S_GC_TRADER_VARS)
        m.V_GC_INTERCONNECTOR = pyo.Var(m.S_GC_INTERCONNECTOR_VARS)
        m.V_GC_REGION = pyo.Var(m.S_GC_REGION_VARS)

        # Generic constraint violation pyo.Variables
        m.V_CV = pyo.Var(m.S_GENERIC_CONSTRAINTS, within=pyo.NonNegativeReals)
        m.V_CV_LHS = pyo.Var(m.S_GENERIC_CONSTRAINTS, within=pyo.NonNegativeReals)
        m.V_CV_RHS = pyo.Var(m.S_GENERIC_CONSTRAINTS, within=pyo.NonNegativeReals)

        # Trader band offer < bid violation
        m.V_CV_TRADER_OFFER = pyo.Var(m.S_TRADER_OFFERS, m.S_BANDS, within=pyo.NonNegativeReals)

        # Trader total capacity < max available violation
        m.V_CV_TRADER_CAPACITY = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)

        # MNSP band offer < bid violation
        m.V_CV_MNSP_OFFER = pyo.Var(m.S_MNSP_OFFERS, m.S_BANDS, within=pyo.NonNegativeReals)

        # MNSP total capacity < max available violation
        m.V_CV_MNSP_CAPACITY = pyo.Var(m.S_MNSP_OFFERS, within=pyo.NonNegativeReals)

        # Ramp rate constraint violation pyo.Variables
        m.V_CV_TRADER_RAMP_UP = pyo.Var(m.S_TRADERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_RAMP_DOWN = pyo.Var(m.S_TRADERS, within=pyo.NonNegativeReals)

        # FCAS trapezium violation pyo.Variables
        m.V_CV_TRADER_FCAS_TRAPEZIUM = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_FCAS_AS_PROFILE_1 = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_FCAS_AS_PROFILE_2 = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_FCAS_AS_PROFILE_3 = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)

        # FCAS joint ramping constraint violation pyo.Variables
        m.V_CV_TRADER_FCAS_JOINT_RAMPING_UP = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_FCAS_JOINT_RAMPING_DOWN = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)

        # FCAS joint capacity constraint violation pyo.Variables
        m.V_CV_TRADER_FCAS_JOINT_CAPACITY_UP = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_TRADER_FCAS_JOINT_CAPACITY_DOWN = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)

        # FCAS joint regulating capacity constraint violation pyo.Variables
        m.V_CV_JOINT_REGULATING_CAPACITY_UP = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)
        m.V_CV_JOINT_REGULATING_CAPACITY_DOWN = pyo.Var(m.S_TRADER_OFFERS, within=pyo.NonNegativeReals)

        # Interconnector forward and reverse flow constraint violation
        m.V_CV_INTERCONNECTOR_FORWARD = pyo.Var(m.S_INTERCONNECTORS, within=pyo.NonNegativeReals)
        m.V_CV_INTERCONNECTOR_REVERSE = pyo.Var(m.S_INTERCONNECTORS, within=pyo.NonNegativeReals)

        # Loss model breakpoints and intervals
        m.V_LOSS = pyo.Var(m.S_INTERCONNECTORS)
        m.V_LOSS_LAMBDA = pyo.Var(m.S_INTERCONNECTOR_LOSS_MODEL_BREAKPOINTS, within=pyo.NonNegativeReals)
        m.V_LOSS_Y = pyo.Var(m.S_INTERCONNECTOR_LOSS_MODEL_INTERVALS, within=pyo.Binary)

        # Flow between region and interconnector connection points
        m.V_FLOW_FROM_CP = pyo.Var(m.S_INTERCONNECTORS)
        m.V_FLOW_TO_CP = pyo.Var(m.S_INTERCONNECTORS)

        return m

    @staticmethod
    def define_expressions(m, data):
        """Define model expressions"""

        # Cost function expressions
        m = define_cost_function_expressions(m)
        m = define_generic_constraint_expressions(m, data)
        m = define_constraint_violation_penalty_expressions(m)
        m = define_aggregate_power_expressions(m)

        return m

    @staticmethod
    def define_constraints(m):
        """Define model constraints"""

        t0 = time.time()

        # Ensure offer bands aren't violated
        print('Starting to define constraints:', time.time() - t0)
        m = define_offer_constraints(m)
        print('Defined offer constraints:', time.time() - t0)

        # Construct generic constraints and link variables to those found in objective
        m = define_generic_constraints(m)
        print('Defined generic constraints:', time.time() - t0)

        # Construct unit constraints (e.g. ramp rate constraints)
        m = define_unit_constraints(m)
        print('Defined unit constraints:', time.time() - t0)

        # Construct region power balance constraints
        m = define_region_constraints(m)
        print('Defined region constraints:', time.time() - t0)

        # Construct interconnector constraints
        m = define_interconnector_constraints(m)
        print('Defined interconnector constraints:', time.time() - t0)

        # Construct FCAS constraints
        m = define_fcas_constraints(m)
        print('Defined FCAS constraints:', time.time() - t0)

        # SOS2 interconnector loss model constraints
        m = define_loss_model_constraints(m)
        print('Defined loss model constraints:', time.time() - t0)

        return m

    @staticmethod
    def define_objective(m):
        """Define model objective"""

        # Total cost for energy and ancillary services
        m.OBJECTIVE = pyo.Objective(expr=sum(m.E_TRADER_COST_FUNCTION[t] for t in m.S_TRADER_OFFERS)
                                         + sum(m.E_MNSP_COST_FUNCTION[t] for t in m.S_MNSP_OFFERS)
                                         + m.E_CV_TOTAL_PENALTY
                                    ,
                                    sense=pyo.minimize)

        return m

    @staticmethod
    def fix_interconnector_flow_solution(m, data):
        """Fix interconnector solution to observed values"""

        for i in m.S_GC_INTERCONNECTOR_VARS:
            observed_flow = float(data['solution']['interconnectors'][i]['@Flow'])
            m.V_GC_INTERCONNECTOR[i].fix(observed_flow)

        return m

    @staticmethod
    def fix_interconnector_loss_solution(m, data):
        """Fix interconnector solution to observed values"""

        for i in m.S_GC_INTERCONNECTOR_VARS:
            observed_flow = float(data['solution']['interconnectors'][i]['@Losses'])
            m.V_LOSS[i].fix(observed_flow)

        return m

    @staticmethod
    def fix_fcas_solution(m, data):
        """Fix FCAS solution"""

        # Map between NEMDE output keys and keys used in solution dictionary
        key_map = {'ENOF': '@EnergyTarget', 'LDOF': '@EnergyTarget',
                   'R6SE': '@R6Target', 'R60S': '@R60Target', 'R5MI': '@R5Target', 'R5RE': '@R5RegTarget',
                   'L6SE': '@L6Target', 'L60S': '@L60Target', 'L5MI': '@L5Target', 'L5RE': '@L5RegTarget'}

        for i, j in m.S_TRADER_FCAS_OFFERS:
            m.V_TRADER_TOTAL_OFFER[(i, j)].fix(data['solution']['traders'][i][key_map[j]])

        return m

    @staticmethod
    def fix_energy_solution(m, data):
        """Fix FCAS solution"""

        # Map between NEMDE output keys and keys used in solution dictionary
        key_map = {'ENOF': '@EnergyTarget', 'LDOF': '@EnergyTarget',
                   'R6SE': '@R6Target', 'R60S': '@R60Target', 'R5MI': '@R5Target', 'R5RE': '@R5RegTarget',
                   'L6SE': '@L6Target', 'L60S': '@L60Target', 'L5MI': '@L5Target', 'L5RE': '@L5RegTarget'}

        for i, j in m.S_TRADER_ENERGY_OFFERS:
            m.V_TRADER_TOTAL_OFFER[(i, j)].fix(data['solution']['traders'][i][key_map[j]])

        return m

    @staticmethod
    def fix_selected_trader_solution(m, data):
        """Fix FCAS solution"""

        # Map between NEMDE output keys and keys used in solution dictionary
        key_map = {'ENOF': '@EnergyTarget', 'LDOF': '@EnergyTarget',
                   'R6SE': '@R6Target', 'R60S': '@R60Target', 'R5MI': '@R5Target', 'R5RE': '@R5RegTarget',
                   'L6SE': '@L6Target', 'L60S': '@L60Target', 'L5MI': '@L5Target', 'L5RE': '@L5RegTarget'}

        for i, j in [('UPPTUMUT', 'ENOF'), ('MURRAY', 'ENOF')]:
            m.V_TRADER_TOTAL_OFFER[(i, j)].fix(data['solution']['traders'][i][key_map[j]])

        return m

    def construct_model(self, data):
        """Create model object"""

        # Initialise model
        t0 = time.time()
        m = pyo.ConcreteModel()

        # Define model components
        m = self.define_sets(m, data)
        m = self.define_parameters(m, data)
        m = self.define_variables(m)
        m = self.define_expressions(m, data)
        m = self.define_constraints(m)
        m = self.define_objective(m)
        print('Constructed model in:', time.time() - t0)

        # Fixing interconnector and FCAS solutions
        # m = self.fix_selected_trader_solution(m, data)
        # m = self.fix_interconnector_flow_solution(m, data)
        # m = self.fix_interconnector_loss_solution(m, data)
        # m = self.fix_energy_solution(m, data)
        # m = self.fix_fcas_solution(m, data)

        return m

    @staticmethod
    def solve_model(m):
        """Solve model"""
        # Setup solver
        solver_options = {}  # 'MIPGap': 0.0005,
        opt = pyo.SolverFactory('cplex', solver_io='lp')

        # Solve model
        t0 = time.time()

        print('Starting solve:', time.time() - t0)
        solve_status = opt.solve(m, tee=True, options=solver_options, keepfiles=False)
        print('Finished solve:', time.time() - t0)

        return m, solve_status


if __name__ == '__main__':
    # Directory containing case data
    data_directory = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.path.pardir,
                                  os.path.pardir, os.path.pardir, 'nemweb', 'Reports', 'Data_Archive', 'NEMDE',
                                  'zipped')

    # NEMDE model object
    nemde = NEMDEModel()

    # Case data in json format
    case_data_json = utils.loaders.load_dispatch_interval_json(data_directory, 2019, 10, 10, 1)

    # Get NEMDE model data as a Python dictionary
    cdata = json.loads(case_data_json)

    # # Drop keys
    # for k in ['ConstraintScadaDataCollection', 'GenericEquationCollection']:
    #     cdata['NEMSPDCaseFile']['NemSpdInputs'].pop(k)
    # with open('example.json', 'w') as f:
    #     json.dump(cdata, f)

    case_data = utils.data.parse_case_data_json(case_data_json)

    # Construct model
    nemde_model = nemde.construct_model(case_data)

    # Solve model
    nemde_model, status = nemde.solve_model(nemde_model)

    # Extract solution
    solution = utils.solution.get_model_solution(nemde_model)

    # with open('solution_example.json', 'w') as f:
    #     json.dump(solution, f)

    # Difference
    trader_solution, df_trader_solution = utils.analysis.check_trader_solution(cdata, solution)

    # Interconnector solutions
    interconnector_flow_solution = utils.analysis.check_interconnector_solution(cdata, solution, 'Flow')
    interconnector_losses_solution = utils.analysis.check_interconnector_solution(cdata, solution, 'Losses')

    # Plot interconnector solution
    utils.analysis.plot_interconnector_solution(cdata, solution)
    utils.analysis.plot_trader_solution_difference(cdata, solution)

    # FCAS solution
    # utils.analysis.plot_fcas_solution(cdata, case_data, solution)

    # import pandas as pd
    # import matplotlib.pyplot as plt
    #
    # df = pd.DataFrame(
    #     {k: {'loss': v} for k, v in nemde_model.P_INTERCONNECTOR_LOSS_MODEL_BREAKPOINT_Y.items()}).T.sort_index()
    # for i in df.index.levels[0]:
    #     df.xs(i, level=0).plot(title=i)
    # plt.show()

    # Error metric - mean square error for each offer type
    print(df_trader_solution['abs_difference'].apply(lambda x: x ** 2).reset_index()
          .groupby('level_1')['abs_difference'].mean().rename_axis('mse').round(4))
