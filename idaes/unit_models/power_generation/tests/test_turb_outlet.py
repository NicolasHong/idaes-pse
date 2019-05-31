##############################################################################
# Institute for the Design of Advanced Energy Systems Process Systems
# Engineering Framework (IDAES PSE Framework) Copyright (c) 2018-2019, by the
# software owners: The Regents of the University of California, through
# Lawrence Berkeley National Laboratory,  National Technology & Engineering
# Solutions of Sandia, LLC, Carnegie Mellon University, West Virginia
# University Research Corporation, et al. All rights reserved.
#
# Please see the files COPYRIGHT.txt and LICENSE.txt for full copyright and
# license information, respectively. Both files are also available online
# at the URL "https://github.com/IDAES/idaes-pse".
##############################################################################
"""
Tests for turbine outlet model.

Author: John Eslick
"""
import pytest

from pyomo.environ import ConcreteModel, SolverFactory, TransformationFactory

from idaes.core import FlowsheetBlock
from idaes.unit_models.power_generation import TurbineOutletStage
from idaes.property_models import iapws95_ph
from idaes.property_models.iapws95 import iapws95_available
from idaes.core.util.model_statistics import (
        calculate_degrees_of_freedom,
        equality_constraint_set,
        activated_component_set)

prop_available = iapws95_available()

# See if ipopt is available and set up solver
if SolverFactory('ipopt').available():
    solver = SolverFactory('ipopt')
    solver.options = {'tol': 1e-6}
else:
    solver = None

@pytest.fixture()
def build_turbine():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(default={"dynamic": False})
    m.fs.properties = iapws95_ph.Iapws95ParameterBlock()
    m.fs.turb = TurbineOutletStage(default={"property_package": m.fs.properties})
    return m

@pytest.fixture()
def build_turbine_dyn():
    m = ConcreteModel()
    m.fs = FlowsheetBlock(default={"dynamic": True})
    m.fs.properties = iapws95_ph.Iapws95ParameterBlock()
    m.fs.turb = TurbineOutletStage(default={
        "dynamic": False,
        "property_package": m.fs.properties})
    return m

def test_basic_build(build_turbine):
    """Make a turbine model and make sure it doesn't throw exception"""
    m = build_turbine

@pytest.mark.skipif(not prop_available, reason="IAPWS not available")
@pytest.mark.skipif(solver is None, reason="Solver not available")
def test_initialize(build_turbine):
    """Initialize a turbine model"""
    m = build_turbine
    # set inlet
    m.fs.turb.inlet.enth_mol[0].value = 47115
    m.fs.turb.inlet.flow_mol[0].value = 15000
    m.fs.turb.inlet.pressure[0].value = 8e4

    m.fs.turb.initialize(outlvl=1)

    eq_cons = activated_component_set(equality_constraint_set(m))
    for c in eq_cons:
        assert(abs(c.body() - c.lower) < 1e-4)
    assert(calculate_degrees_of_freedom(m)==3) #inlet was't fixed and still shouldn't be
