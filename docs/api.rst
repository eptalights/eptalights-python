..  _api:

API Reference
=============

Function
--------

.. autoclass:: eptalights.models.egimple.function.FunctionModel
    :members:


Step or Instruction
-------------------

.. autoclass:: eptalights.models.egimple.function.EGimpleIRNopModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRAssignModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRCallModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRCondModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRReturnModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRGotoModel
    :members:

.. autoclass:: eptalights.models.egimple.function.EGimpleIRSwitchModel
    :members:

.. autoclass:: eptalights.models.egimple.function.ExprModel
    :members:


Callsite
--------

.. autoclass:: eptalights.models.egimple.callsite.CallsiteModel
    :members:

.. autoclass:: eptalights.models.egimple.callsite.CallsiteManagerModel
    :members:


CFG
---

.. autoclass:: eptalights.models.egimple.cfg.ControlFlowGraphModel
    :members:


Variable
--------

.. autoclass:: eptalights.models.egimple.variable.SSAVariableModel
    :members:

.. autoclass:: eptalights.models.egimple.variable.VariableModel
    :members:

.. autoclass:: eptalights.models.egimple.variable.VariableManagerModel
    :members:


Tokenized Operands
------------------

.. autoclass:: eptalights.models.egimple.tokenized_operand.TokenizedOperandModel
    :members:

.. autoclass:: eptalights.models.egimple.tokenized_operand.TokenModel
    :members:


Enum Types
----------

.. autoclass:: eptalights.models.egimple.enum_types.VarType
    :members:

.. autoclass:: eptalights.models.egimple.enum_types.TokenType
    :members:

.. .. autoclass:: eptalights.models.egimple.enum_types.ExprType
..     :members:

.. .. autoclass:: eptalights.models.egimple.enum_types.OpType
..     :members:


Dataflow
--------

.. autoclass:: eptalights.models.egimple.dataflow.SinkResultType
    :members:

.. autoclass:: eptalights.models.egimple.dataflow.DataflowEventModel
    :members:

.. autoclass:: eptalights.models.egimple.dataflow.DataflowStateModel
    :members:

.. autoclass:: eptalights.models.egimple.dataflow.DataflowPathModel
    :members:

.. autoclass:: eptalights.models.egimple.dataflow.DataflowRequestModel
    :members:

.. autoclass:: eptalights.models.egimple.dataflow.DataflowResponseModel
    :members:
